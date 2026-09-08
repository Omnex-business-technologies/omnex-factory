"""P6 — security guardrails.

Prompt-injection resistance, reversible PII redaction, output filtering, rate
limiting and sandboxed execution, composed into one object that owns both
directions of a request.

Two positions here differ from the usual guardrail library, and both are stated
in the modules rather than implied:

- **Injection defence is structural, not lexical.** Provenance travels with
  text, untrusted content can never reach the system role, and it is fenced with
  a per-request nonce it cannot forge. The detector is defence in depth with a
  measured false-positive rate, not the control.
- **Redaction is reversible.** One-way redaction makes conversational systems
  useless — the model answers about `‹EMAIL_1›` and so does the product. The
  vault restores on the way out, and only tokens it actually issued.
"""

from .injection import (
    InjectionDetector,
    InjectionFinding,
    PromptAssembler,
    Provenance,
    Segment,
)
from .middleware import GuardPolicy, Guardrail, InboundResult, OutboundResult
from .output import Audience, OutputFinding, OutputGuard, Severity
from .pii import PiiKind, PiiMatch, PiiPolicy, PiiVault, detect, luhn_ok
from .ratelimit import Decision, RateLimit, RateLimiter
from .sandbox import SandboxPolicy, SandboxResult, run_python

__all__ = [
    "Audience",
    "Decision",
    "GuardPolicy",
    "Guardrail",
    "InboundResult",
    "InjectionDetector",
    "InjectionFinding",
    "OutboundResult",
    "OutputFinding",
    "OutputGuard",
    "PiiKind",
    "PiiMatch",
    "PiiPolicy",
    "PiiVault",
    "PromptAssembler",
    "Provenance",
    "RateLimit",
    "RateLimiter",
    "SandboxPolicy",
    "SandboxResult",
    "Segment",
    "Severity",
    "detect",
    "luhn_ok",
    "run_python",
]
