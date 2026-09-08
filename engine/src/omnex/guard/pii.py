"""PII detection and REVERSIBLE redaction.

Most redaction implementations are one-way, which quietly makes them useless for
anything conversational. Redact "email ada@example.com about the invoice" to
"email [EMAIL] about the invoice", and the model's reply is "I have drafted a
message to [EMAIL]" — now you either ship a placeholder to a user or you gave up
and sent the real address to the provider after all.

So this is a **vault**: redaction issues stable placeholder tokens, keeps the
mapping in-process, and restores them on the way back out. The model reasons
about `‹EMAIL_1›` and never sees the address; the user sees the address and never
sees the token.

Three properties make it safe rather than merely convenient, and each is tested:

**Consistency.** The same value always gets the same token within one vault, so
"forward Ada's email to Ada" survives as one entity rather than two, and the
model can still reason about identity. Different values never share a token.

**Restoration is closed.** `restore()` resolves only tokens *this vault issued*.
A model that emits `‹EMAIL_7›` out of thin air — because it pattern-matched the
format, or because someone asked it to — gets nothing back. Without that rule the
placeholder scheme becomes an oracle: guess token names, get real values.

**Validation, not just pattern matching.** A sixteen-digit number is not a card
number; `4111 1111 1111 1111` passes the Luhn check and `4111 1111 1111 1112`
does not. Redacting every long digit string destroys order numbers, invoice ids
and part numbers, and the resulting false-positive rate is what gets a redaction
layer switched off. The corpus in `tests/data` measures precision and recall
rather than assuming them.

Detection is regex plus checksum, deliberately. A NER model would catch more
names, cost a model call per request on the hot path, and still miss; the honest
position is that this catches *structured* identifiers reliably and free-form
names not at all, and `PiiPolicy.allow_freeform_names` exists so a caller states
which risk they are accepting.
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from enum import StrEnum

__all__ = ["PiiKind", "PiiMatch", "PiiPolicy", "PiiVault", "detect", "luhn_ok"]


class PiiKind(StrEnum):
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    CARD = "CARD"
    IBAN = "IBAN"
    #: Croatian personal identification number — 11 digits with a checksum.
    #: Included because this repo's operator is in Croatia and a generic
    #: "national id" pattern is exactly the kind that fires on order numbers.
    OIB = "OIB"
    IP = "IP"
    SSN = "SSN"
    DOB = "DOB"


@dataclass(frozen=True)
class PiiMatch:
    kind: PiiKind
    value: str
    start: int
    end: int


# ── validators ────────────────────────────────────────────────────────────


def luhn_ok(digits: str) -> bool:
    """Luhn check. The difference between a card number and an order number."""
    nums = [int(c) for c in digits if c.isdigit()]
    if len(nums) < 12:
        return False
    total = 0
    for i, digit in enumerate(reversed(nums)):
        if i % 2 == 1:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10 == 0


def _oib_ok(digits: str) -> bool:
    """ISO 7064 MOD 11,10 — the checksum a Croatian OIB carries."""
    if len(digits) != 11 or not digits.isdigit():
        return False
    remainder = 10
    for char in digits[:10]:
        remainder = (remainder + int(char)) % 10 or 10
        remainder = (remainder * 2) % 11
    check = (11 - remainder) % 10
    return check == int(digits[10])


def _iban_ok(value: str) -> bool:
    """ISO 13616 MOD-97. Cheap, and removes nearly every false positive."""
    compact = re.sub(r"\s+", "", value).upper()
    if len(compact) < 15 or not compact[:2].isalpha():
        return False
    rearranged = compact[4:] + compact[:4]
    digits = "".join(str(int(c, 36)) for c in rearranged if c.isalnum())
    try:
        return int(digits) % 97 == 1
    except ValueError:
        return False


# ── patterns ──────────────────────────────────────────────────────────────

_PATTERNS: list[tuple[PiiKind, re.Pattern[str]]] = [
    (PiiKind.EMAIL, re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]{2,}\b")),
    (PiiKind.IBAN, re.compile(r"\b[A-Z]{2}\d{2}[ ]?(?:[A-Z0-9]{4}[ ]?){2,7}[A-Z0-9]{1,4}\b")),
    (PiiKind.CARD, re.compile(r"\b(?:\d[ -]?){12,18}\d\b")),
    (PiiKind.OIB, re.compile(r"\b\d{11}\b")),
    (PiiKind.SSN, re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    # E.164 and common national forms. Requires a separator or a leading +, so a
    # bare run of digits is left to the card/OIB validators instead.
    (
        PiiKind.PHONE,
        re.compile(r"(?:\+\d{1,3}[ -]?)?(?:\(\d{1,4}\)[ -]?|\d{2,4}[ -])\d{3}[ -]?\d{3,4}\b"),
    ),
    (PiiKind.IP, re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")),
    (
        PiiKind.DOB,
        re.compile(r"\b(?:0?[1-9]|[12]\d|3[01])[./-](?:0?[1-9]|1[0-2])[./-](?:19|20)\d{2}\b"),
    ),
]

_VALIDATORS = {
    PiiKind.CARD: luhn_ok,
    PiiKind.OIB: _oib_ok,
    PiiKind.IBAN: _iban_ok,
}


@dataclass
class PiiPolicy:
    """Which kinds to act on, and what the caller is knowingly accepting."""

    kinds: frozenset[PiiKind] = field(default_factory=lambda: frozenset(PiiKind))
    #: Stated, not implied: this detector does not find free-form personal
    #: names. Leaving it True documents that the caller accepts that gap rather
    #: than believing it does not exist.
    allow_freeform_names: bool = True

    def covers(self, kind: PiiKind) -> bool:
        return kind in self.kinds


def detect(text: str, policy: PiiPolicy | None = None) -> list[PiiMatch]:
    """Every validated PII match, longest-first, with overlaps resolved.

    Overlap resolution matters: an IBAN contains a run of digits that the card
    pattern also matches, and emitting both means the second redaction corrupts
    the first. Longest match wins, which is right in every observed collision.
    """
    policy = policy or PiiPolicy()
    found: list[PiiMatch] = []

    for kind, pattern in _PATTERNS:
        if not policy.covers(kind):
            continue
        validator = _VALIDATORS.get(kind)
        for match in pattern.finditer(text):
            value = match.group(0)
            if validator and not validator(value):
                continue
            found.append(PiiMatch(kind, value, match.start(), match.end()))

    # Longest first, so the longer of two overlapping matches claims the span.
    # A distinct name from the `re.Match` above on purpose: `.end` is a method
    # on one and an integer field on the other, and reusing the name makes a
    # type error look like working code.
    resolved: list[PiiMatch] = []
    for candidate in sorted(found, key=lambda m: (-(m.end - m.start), m.start)):
        overlaps = any(
            not (candidate.end <= kept.start or candidate.start >= kept.end) for kept in resolved
        )
        if not overlaps:
            resolved.append(candidate)
    return sorted(resolved, key=lambda m: m.start)


class PiiVault:
    """Redacts to stable placeholders and restores only what it issued."""

    #: Guillemets rather than square brackets: `[EMAIL_1]` collides with
    #: markdown links and with the placeholder syntax half of all prompt
    #: templates already use, and a collision means restoring text the vault
    #: never redacted.
    OPEN = "‹"
    CLOSE = "›"

    _TOKEN = re.compile(r"‹([A-Z]+)_(\d+)›")

    def __init__(self, policy: PiiPolicy | None = None) -> None:
        self.policy = policy or PiiPolicy()
        self._to_token: dict[tuple[PiiKind, str], str] = {}
        self._to_value: dict[str, str] = {}
        self._counts: dict[PiiKind, int] = {}

    # ── redaction ─────────────────────────────────────────────────────────
    def redact(self, text: str) -> str:
        matches = detect(text, self.policy)
        if not matches:
            return text
        out: list[str] = []
        cursor = 0
        for match in matches:
            out.append(text[cursor : match.start])
            out.append(self._token_for(match))
            cursor = match.end
        out.append(text[cursor:])
        return "".join(out)

    def _token_for(self, match: PiiMatch) -> str:
        key = (match.kind, match.value)
        existing = self._to_token.get(key)
        if existing is not None:
            return existing  # consistency: one entity, one token
        index = self._counts.get(match.kind, 0) + 1
        self._counts[match.kind] = index
        token = f"{self.OPEN}{match.kind.value}_{index}{self.CLOSE}"
        self._to_token[key] = token
        self._to_value[token] = match.value
        return token

    # ── restoration ───────────────────────────────────────────────────────
    def restore(self, text: str) -> str:
        """Put the real values back — but only for tokens this vault issued.

        An unknown token is left verbatim rather than resolved or stripped. If
        a model can invent `‹EMAIL_7›` and receive a real address, the scheme
        stops being redaction and becomes a lookup oracle; leaving it visible
        means the surprise shows up in the output where someone will notice.
        """
        return self._TOKEN.sub(
            lambda m: self._to_value.get(m.group(0), m.group(0)),
            text,
        )

    # ── introspection ─────────────────────────────────────────────────────
    @property
    def issued(self) -> int:
        return len(self._to_value)

    def summary(self) -> dict[str, int]:
        """Counts by kind — safe to log, unlike anything else here."""
        return {kind.value: count for kind, count in sorted(self._counts.items())}

    def tokens(self) -> Iterable[str]:
        return tuple(self._to_value)

    def holds(self, token: str) -> bool:
        return token in self._to_value
