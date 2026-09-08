"""The two steps an n8n workflow runs before it touches an order.

    python -m omnex.pipeline verify --timestamp T --signature S < body.json
    python -m omnex.pipeline claim --store .claims --event-id ID

`n8n_bindings.json` names these commands. They exist as a CLI rather than as
nodes because an n8n `executeCommand` node is the one place this repository's own
code can run inside somebody else's workflow without shipping a custom node, and
because the shape of a command — stdin, argv, exit code — is knowable from here,
which the storefront APIs are not.

## Exit codes are the interface

    0   proceed
    1   refused: bad signature, replayed timestamp, missing secret, no event id
    3   already delivered — not an error, and not a reason to alarm

`3` is separate on purpose. A redelivery is the normal case; collapsing it into
`1` makes every retry look like a failure and teaches whoever watches the
workflow to ignore the failures.

## The secret is read from the environment, never from argv

`OMNEX_WEBHOOK_SECRET`. There is no `--secret` flag and adding one would be a
regression: arguments are visible in `ps` to every user on the host, and n8n
writes the command it ran into its own execution log, which is then a copy of the
signing key sitting in a database somebody backs up.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from ..core.errors import OmnexError
from .claim import Claims
from .webhook import WebhookVerifier

SECRET_ENV = "OMNEX_WEBHOOK_SECRET"

PROCEED = 0
REFUSED = 1
ALREADY_DELIVERED = 3


def _verify(args: argparse.Namespace) -> int:
    secret = os.environ.get(SECRET_ENV, "")
    if not secret:
        print(
            f"{SECRET_ENV} is not set. The secret is read from the environment and "
            "never from a flag: arguments are visible in `ps`, and n8n records the "
            "command it ran in its own execution log.",
            file=sys.stderr,
        )
        return REFUSED

    body = sys.stdin.buffer.read()
    verifier = WebhookVerifier(secret=secret)
    try:
        verifier.verify(args.timestamp, body, args.signature)
        event = verifier.parse(body, kind_field=args.kind_field, id_field=args.id_field)
    except OmnexError as exc:
        print(f"refused: {exc.message}", file=sys.stderr)
        return REFUSED

    # Only the identifying fields go to stdout. The body is already in n8n;
    # echoing it here would put a paid order's contents into a second log.
    print(json.dumps({"event_id": event.event_id, "kind": event.kind}))
    return PROCEED


def _claim(args: argparse.Namespace) -> int:
    claims = Claims(directory=Path(args.store))
    try:
        outcome = claims.claim(args.event_id)
    except OmnexError as exc:
        print(f"refused: {exc.message}", file=sys.stderr)
        return REFUSED

    print(
        json.dumps(
            {
                "event_id": outcome.event_id,
                "first": outcome.first,
                "claimed_at": outcome.claimed_at,
            }
        )
    )
    return PROCEED if outcome.first else ALREADY_DELIVERED


def _release(args: argparse.Namespace) -> int:
    """For a caller that knows its failure was transient. Never automatic."""
    released = Claims(directory=Path(args.store)).release(args.event_id)
    print(json.dumps({"event_id": args.event_id, "released": released}))
    return PROCEED


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m omnex.pipeline", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    verify = sub.add_parser("verify", help="verify a webhook signature; body on stdin")
    verify.add_argument("--timestamp", required=True)
    verify.add_argument("--signature", required=True)
    verify.add_argument("--id-field", default="id", help="payload field holding the sender's id")
    verify.add_argument("--kind-field", default="type")
    verify.set_defaults(run=_verify)

    claim = sub.add_parser("claim", help="claim an event id once; exit 3 if already claimed")
    claim.add_argument("--store", required=True, help="directory holding one file per claim")
    claim.add_argument("--event-id", required=True)
    claim.set_defaults(run=_claim)

    release = sub.add_parser("release", help="un-claim an event so a retry can land")
    release.add_argument("--store", required=True)
    release.add_argument("--event-id", required=True)
    release.set_defaults(run=_release)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    exit_code: int = args.run(args)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
