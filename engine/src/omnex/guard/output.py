"""Checks on what the system is about to emit.

Inbound guardrails get the attention; outbound is where the damage actually
happens. The rule this repo learned the hard way is recorded in
`lib/core/agents/guardrails.ts`: an agent published a stale cold pitch to a
named company, including their funding amount, as a public post. The generation
was fine. There was simply no gate between "text exists" and "text is public".

Four families, each earning its place by being a thing that has gone wrong
rather than a thing that could:

**Leaked credentials.** Models echo their context. If a key ever reached the
prompt — from an env dump, a pasted config, a tool result — it can come back out
in the answer, and from there into a log, a ticket, or a web page.

**Unfilled template placeholders.** `Hi {{first_name}},` reaching a customer is
the single most common visible failure of a generated-content system, and it is
trivially detectable before sending.

**Wrong-audience leakage.** Text addressed to one named recipient being
published to everyone. This is the failure quoted above, and it is why the check
takes an explicit `audience` rather than guessing.

**Fabricated citations.** A claim carrying `[p. 41]` when the source has 30
pages. P1 verifies citations against the retrieved evidence; this catches the
structural impossibility cheaply and without the corpus.

Every check returns findings rather than raising. The caller decides what
blocks, because the right policy genuinely differs: a draft shown to its author
should surface a leaked key as a warning, while the same text going to a public
endpoint must be refused. One policy for both is wrong for one of them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum

__all__ = ["Audience", "OutputFinding", "OutputGuard", "Severity"]


class Severity(StrEnum):
    BLOCK = "block"
    WARN = "warn"


class Audience(StrEnum):
    """Who is about to see this. Determines how strict the checks are."""

    #: Shown back to the person who asked. Leaks are recoverable.
    AUTHOR = "author"
    #: Sent to a specific named third party.
    RECIPIENT = "recipient"
    #: Published where anyone can read it. Nothing is recoverable here.
    PUBLIC = "public"


@dataclass(frozen=True)
class OutputFinding:
    rule: str
    severity: Severity
    message: str
    #: A short window, never the whole document — findings go to logs, which
    #: usually have weaker access controls than the store the text came from.
    evidence: str = ""


# Ordered most-specific first, so a generic pattern cannot claim a known key
# type and report it under the wrong rule name.
_SECRETS: list[tuple[str, re.Pattern[str]]] = [
    ("stripe_live_key", re.compile(r"\bsk_live_[A-Za-z0-9]{16,}")),
    ("stripe_test_key", re.compile(r"\bsk_test_[A-Za-z0-9]{16,}")),
    ("supabase_secret", re.compile(r"\bsb_secret_[A-Za-z0-9_-]{16,}")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{32,}")),
    ("anthropic_key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{24,}")),
    ("hf_token", re.compile(r"\bhf_[A-Za-z0-9]{30,}")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}")),
    ("bearer_token", re.compile(r"\bBearer\s+[A-Za-z0-9._~+/-]{30,}", re.IGNORECASE)),
    ("private_key_block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

#: Every templating syntax in common use. A generated document should contain
#: none of them by the time it is sent.
_PLACEHOLDER = re.compile(
    r"(\{\{[\w.\s|]+\}\}|\$\{[\w.]+\}|\[(?:FIRST_NAME|LAST_NAME|COMPANY|NAME|EMAIL|X{2,})\]|<INSERT[^>]*>)",
    re.IGNORECASE,
)

_CITATION = re.compile(r"\[(?:p\.?|page)\s*(\d+)\]", re.IGNORECASE)

_GREETING = re.compile(r"^\s*(hi|hello|dear|hey)\s+([A-Z][a-z]+)", re.IGNORECASE | re.MULTILINE)


@dataclass
class OutputGuard:
    """Runs the outbound checks. Returns findings; never decides for the caller."""

    #: Highest page number that can legitimately be cited. Zero disables the check.
    max_page: int = 0
    #: The single recipient this text is addressed to, when there is one.
    recipient: str = ""

    def check(self, text: str, audience: Audience = Audience.AUTHOR) -> list[OutputFinding]:
        findings: list[OutputFinding] = []
        findings.extend(self._secrets(text))
        findings.extend(self._placeholders(text, audience))
        findings.extend(self._citations(text))
        findings.extend(self._audience(text, audience))
        return findings

    def blocks(self, findings: list[OutputFinding]) -> bool:
        return any(f.severity is Severity.BLOCK for f in findings)

    def redact(self, text: str) -> str:
        """Strip anything that must never be stored, for safe logging."""
        out = text
        for rule, pattern in _SECRETS:
            out = pattern.sub(f"‹redacted:{rule}›", out)
        return out

    # ── individual checks ─────────────────────────────────────────────────
    def _secrets(self, text: str) -> list[OutputFinding]:
        findings = []
        for rule, pattern in _SECRETS:
            match = pattern.search(text)
            if match:
                findings.append(
                    OutputFinding(
                        rule=rule,
                        severity=Severity.BLOCK,  # never audience-dependent
                        message="output contains what looks like a live credential",
                        evidence=_window(text, match.start()),
                    )
                )
        return findings

    def _placeholders(self, text: str, audience: Audience) -> list[OutputFinding]:
        match = _PLACEHOLDER.search(text)
        if not match:
            return []
        return [
            OutputFinding(
                rule="unfilled_placeholder",
                # Harmless in a draft the author is about to edit; embarrassing
                # and irreversible once sent.
                severity=Severity.WARN if audience is Audience.AUTHOR else Severity.BLOCK,
                message=f"template placeholder {match.group(0)!r} was never filled in",
                evidence=_window(text, match.start()),
            )
        ]

    def _citations(self, text: str) -> list[OutputFinding]:
        if self.max_page <= 0:
            return []
        findings = []
        for match in _CITATION.finditer(text):
            page = int(match.group(1))
            if page > self.max_page or page < 1:
                findings.append(
                    OutputFinding(
                        rule="impossible_citation",
                        severity=Severity.BLOCK,
                        message=f"cites page {page} of a {self.max_page}-page source",
                        evidence=_window(text, match.start()),
                    )
                )
        return findings

    def _audience(self, text: str, audience: Audience) -> list[OutputFinding]:
        """Catch one-to-one text about to go one-to-many.

        Only meaningful for PUBLIC: a personal greeting is correct in a message
        to that person and wrong on a page anyone can read. This exists because
        it happened.
        """
        if audience is not Audience.PUBLIC:
            return []
        match = _GREETING.search(text)
        if not match:
            return []
        return [
            OutputFinding(
                rule="addressed_to_one_published_to_all",
                severity=Severity.BLOCK,
                message=f"text greets {match.group(2)!r} but is being published publicly",
                evidence=_window(text, match.start()),
            )
        ]


def _window(text: str, at: int, length: int = 60) -> str:
    start = max(0, at - 10)
    return re.sub(r"\s+", " ", text[start : start + length]).strip()
