"""The guardrail pipeline: one object that owns both directions of a request.

Inbound and outbound are deliberately not separate helpers a caller wires up
themselves, because the two are coupled by state that has to survive between
them — the PII vault. Redaction on the way in is worthless if the way out
forgets to restore, and a caller who has to remember both will eventually add a
code path that only does one.

Order matters and is fixed:

1. **Rate limit**, first, and with `peek` semantics until the request is known
   to be servable. Checking cheaply before doing expensive work is the point;
   consuming quota for a request that is then refused for another reason bills
   a tenant for work that never ran.
2. **Redact PII**, before any content reaches a model or a log. Everything
   downstream — traces, prompt caches, provider logs — sees tokens.
3. **Assemble with provenance**, so untrusted content is fenced and cannot
   reach the system role.
4. …the model call happens outside this object…
5. **Check the output**, against the audience it is destined for.
6. **Restore PII**, last, so the real values exist only in the final response
   and never in anything that was persisted along the way.

Step 6 after step 5 is not arbitrary: running the output checks on the redacted
text means a leaked credential is inspected in the form it will be logged in,
and it means the secret scanner does not itself have to handle real PII.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from ..core.clock import Clock, SystemClock
from ..core.errors import GuardrailBlocked
from ..llm.types import Message
from .injection import InjectionDetector, InjectionFinding, PromptAssembler, Provenance, Segment
from .output import Audience, OutputFinding, OutputGuard, Severity
from .pii import PiiPolicy, PiiVault
from .ratelimit import Decision, RateLimit, RateLimiter

__all__ = ["GuardPolicy", "Guardrail", "InboundResult", "OutboundResult"]


@dataclass
class GuardPolicy:
    """Everything a deployment can turn up or down, in one place."""

    rate_limit: RateLimit | None = None
    pii: PiiPolicy = field(default_factory=PiiPolicy)
    #: Redact PII before it reaches a model. Off only where the provider is
    #: your own hardware — which the local-first tier (P7) makes achievable.
    redact_pii: bool = True
    #: Refuse untrusted content that scores as an injection attempt. Off by
    #: default: the nonce fence already removes its authority, and blocking on
    #: a detector whose false-positive rate has not been measured on YOUR
    #: traffic takes down legitimate requests. Measure, then enable.
    block_on_injection: bool = False
    #: Highest page number a citation may reference, for P1's outputs.
    max_page: int = 0


@dataclass
class InboundResult:
    messages: list[Message]
    #: Must be carried to `outbound()`. Without it, redaction is one-way and
    #: the answer reaches the user full of placeholder tokens.
    vault: PiiVault
    injection_findings: list[InjectionFinding]
    rate_limit: Decision | None = None
    #: What was redacted, by kind. Safe to log; the values are not.
    pii_summary: dict[str, int] = field(default_factory=dict)


@dataclass
class OutboundResult:
    text: str
    findings: list[OutputFinding]
    blocked: bool

    @property
    def block_reasons(self) -> list[str]:
        return [f.rule for f in self.findings if f.severity is Severity.BLOCK]


class Guardrail:
    """Owns both directions of one request's safety checks."""

    def __init__(
        self,
        policy: GuardPolicy | None = None,
        clock: Clock | None = None,
        detector: InjectionDetector | None = None,
    ) -> None:
        self.policy = policy or GuardPolicy()
        self.clock = clock or SystemClock()
        self.detector = detector or InjectionDetector()
        self._limiter = (
            RateLimiter(self.policy.rate_limit, clock=self.clock)
            if self.policy.rate_limit
            else None
        )

    # ── inbound ───────────────────────────────────────────────────────────
    def inbound(
        self,
        segments: Sequence[Segment],
        rate_key: str = "",
        consume_quota: bool = True,
    ) -> InboundResult:
        """Prepare messages safely. Raises only for a refusal, never for a warning."""
        decision: Decision | None = None
        if self._limiter is not None and rate_key:
            decision = (
                self._limiter.check(rate_key) if consume_quota else self._limiter.peek(rate_key)
            )
            decision.raise_if_limited(rate_key)

        vault = PiiVault(self.policy.pii)
        prepared: list[Segment] = []
        for segment in segments:
            text = vault.redact(segment.text) if self.policy.redact_pii else segment.text
            prepared.append(
                Segment(text=text, provenance=segment.provenance, source=segment.source)
            )

        assembler = PromptAssembler(
            detector=self.detector, block_on_detection=self.policy.block_on_injection
        )
        messages, findings = assembler.assemble(prepared)

        return InboundResult(
            messages=messages,
            vault=vault,
            injection_findings=findings,
            rate_limit=decision,
            pii_summary=vault.summary(),
        )

    # ── outbound ──────────────────────────────────────────────────────────
    def outbound(
        self,
        text: str,
        vault: PiiVault | None = None,
        audience: Audience = Audience.AUTHOR,
        recipient: str = "",
    ) -> OutboundResult:
        """Check, then restore. Checking the redacted form is deliberate."""
        guard = OutputGuard(max_page=self.policy.max_page, recipient=recipient)
        findings = guard.check(text, audience)
        blocked = guard.blocks(findings)

        # Restoration happens only for text that is actually going out. A
        # blocked response must not have real values put back into it, since
        # the next thing that happens to it is being logged.
        restored = text if blocked or vault is None else vault.restore(text)
        return OutboundResult(text=restored, findings=findings, blocked=blocked)

    def outbound_or_raise(
        self,
        text: str,
        vault: PiiVault | None = None,
        audience: Audience = Audience.AUTHOR,
        recipient: str = "",
    ) -> str:
        result = self.outbound(text, vault, audience, recipient)
        if result.blocked:
            raise GuardrailBlocked(
                "output refused by guardrails",
                findings=result.block_reasons,
                audience=str(audience),
            )
        return result.text

    # ── helpers ───────────────────────────────────────────────────────────
    @staticmethod
    def trusted(text: str, source: str = "system") -> Segment:
        return Segment(text, Provenance.TRUSTED, source)

    @staticmethod
    def user(text: str, source: str = "user") -> Segment:
        return Segment(text, Provenance.USER, source)

    @staticmethod
    def untrusted(text: str, source: str = "external") -> Segment:
        """Anything fetched, retrieved, or produced by a tool.

        If you are unsure which of the three a piece of text is, it is this one.
        """
        return Segment(text, Provenance.UNTRUSTED, source)
