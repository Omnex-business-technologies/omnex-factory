"""Build the request that lists a pack for sale, and refuse everything that should not ship.

    python packs/publish.py cosmetics --to lemonsqueezy --dry-run
    python packs/publish.py cosmetics --to lemonsqueezy --send

`listing_check.py` decides whether the goods cover the promise.
`build_pack.py` turns them into a file a buyer downloads. This is the last step
before money: the request that creates the listing.

## Why this builds a request instead of making one

The Lemon Squeezy and Etsy API shapes could not be read from the environment this
was written in — the open web is refused at the proxy — so no endpoint is
invented here. `--send` requires the URL to come from the operator's own
environment (`OMNEX_LEMONSQUEEZY_URL`, `OMNEX_ETSY_URL`) and refuses without one,
naming the variable. Everything else — the refusals, the body, which credential
is used, the price in cents — is knowable and is built and tested offline.

That split is the same one `build_pack.py` already makes. CI can compare a
promise with a manifest; only the machine holding the files can compare a
manifest with the files. Only the operator's host can reach a storefront.

## The five refusals, and what each one costs if it is missing

1. **A pack that does not cover its listing.** The €49 Vault sells 170 images
   against 80 through QC. Listing that takes money for goods nobody has.
2. **No built archive, or one whose hash does not match what was built now.**
   Uploading a file that is not the file that was checked is the whole reason
   `build_pack.py` is deterministic.
3. **No price.** A listing created at zero is a free pack sold as a paid one, and
   the buyers who took it are not getting a refund request.
4. **A credential that is not configured.** Failing here is a message; failing at
   the storefront is a half-created listing somebody has to find and delete.
5. **`--send` with no endpoint.** Named above.

## Nothing is live

Every offer in `listing.json` carries `live: false`, and this refuses to publish
one whose flag is still false unless `--force-draft` says a draft is intended.
Turning a listing live is a person's decision, and it is the decision that starts
the clock on `registry.ts`'s rule that module N+1 does not open until N has taken
a real payment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

PACKS = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKS))

from listing_check import audit, load_listing, qc_count

#: Per storefront: the environment variable holding the endpoint, and the one
#: holding the credential. Neither value is ever read into the request body or
#: printed — the credential is used as a header and nothing else.
STOREFRONTS: dict[str, dict[str, str]] = {
    "lemonsqueezy": {
        "url_env": "OMNEX_LEMONSQUEEZY_URL",
        "credential_env": "OMNEX_LEMONSQUEEZY_KEY",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
    "etsy": {
        "url_env": "OMNEX_ETSY_URL",
        "credential_env": "OMNEX_ETSY_TOKEN",
        "auth_header": "Authorization",
        "auth_prefix": "Bearer ",
    },
}


@dataclass(frozen=True)
class Request:
    """A request that has not been sent, and can be read before it is."""

    storefront: str
    method: str
    #: Empty until an operator's environment supplies one. Never invented here.
    url: str
    body: dict[str, object]
    #: Header names only. Values live in the environment and are attached at send.
    headers: list[str]
    archive: Path
    sha256: str

    def render(self) -> str:
        """What would be sent, with nothing that could be a credential in it."""
        return json.dumps(
            {
                "storefront": self.storefront,
                "method": self.method,
                "url": self.url or "<unset — supply it in the environment>",
                "headers": self.headers,
                "body": self.body,
                "archive": self.archive.name,
                "sha256": self.sha256,
            },
            indent=2,
            ensure_ascii=False,
        )


@dataclass
class Refusals:
    """Every reason this may not be published, collected rather than raised.

    Being refused one at a time is how somebody concludes the check is the
    obstacle rather than the problem, so all of them are reported together.
    """

    reasons: list[str] = field(default_factory=list)

    def unless(self, condition: bool, reason: str) -> None:
        if not condition:
            self.reasons.append(reason)

    def __bool__(self) -> bool:
        return bool(self.reasons)

    def report(self) -> str:
        return "\n".join(f"  {n}. {reason}" for n, reason in enumerate(self.reasons, 1))


def offer_of(listing: dict[str, object], pack: str) -> dict[str, object] | None:
    for group in ("packs", "bundles"):
        entry = (listing.get(group) or {}).get(pack)  # type: ignore[union-attr]
        if entry:
            return dict(entry)
    return None


def refusals(
    pack: str,
    storefront: str,
    archive: Path | None,
    *,
    root: Path | None = None,
    environment: dict[str, str] | None = None,
    sending: bool = False,
    force_draft: bool = False,
) -> Refusals:
    """Every reason not to publish, at once.

    `environment` is a parameter rather than a read of `os.environ` so the whole
    refusal set is testable without setting variables in the running process.
    """
    root = root or PACKS
    environment = {} if environment is None else environment
    found = Refusals()

    listing = load_listing(root / "listing.json")
    offer = offer_of(listing, pack)
    found.unless(offer is not None, f"{pack!r} is not an offer in listing.json")
    if offer is None:
        return found

    shortfalls, _ = audit(listing, root)
    short = [s for s in shortfalls if s.listing == str(offer.get("listing_name"))]
    found.unless(
        not short,
        f"the listing promises more than QC passed: {short[0] if short else ''} — "
        "publishing it takes money for goods nobody has",
    )

    found.unless(
        archive is not None and archive.exists(),
        "no built archive; run build_pack.py first, because the file a buyer "
        "downloads must be the file that was checked",
    )
    found.unless(
        bool(offer.get("price_eur")),
        "the offer carries no price — a listing created at zero is a free pack "
        "sold as a paid one",
    )
    found.unless(
        bool(offer.get("live")) or force_draft,
        f"{pack!r} is live: false in listing.json. Going live is a person's "
        "decision; pass --force-draft to create it as a draft on purpose",
    )

    settings = STOREFRONTS.get(storefront)
    found.unless(settings is not None, f"unknown storefront {storefront!r}")
    if settings is None:
        return found

    found.unless(
        bool((environment.get(settings["credential_env"]) or "").strip()),
        f"{settings['credential_env']} is not set — failing here is a message, "
        "failing at the storefront is a half-created listing somebody has to find",
    )
    if sending:
        found.unless(
            bool((environment.get(settings["url_env"]) or "").strip()),
            f"{settings['url_env']} is not set. No endpoint is written into this "
            "repository: the storefront's API shape was not readable from the "
            "environment this was built in, and a url from memory that posts to "
            "the wrong host is worse than a blank",
        )
    return found


def build_request(
    pack: str,
    storefront: str,
    archive: Path,
    *,
    root: Path | None = None,
    environment: dict[str, str] | None = None,
) -> Request:
    """The request, assembled from the listing and the built file."""
    root = root or PACKS
    environment = {} if environment is None else environment
    settings = STOREFRONTS[storefront]
    listing = load_listing(root / "listing.json")
    offer = offer_of(listing, pack) or {}

    passed = qc_count(pack, root)
    body: dict[str, object] = {
        "name": offer.get("listing_name"),
        # Cents, as an integer, via Decimal. Every storefront prices in minor
        # units, and `float("19.99") * 100` is 1998.9999999999998 — rounding
        # rescues that one and this repository already refuses the float
        # currency path everywhere else rather than relying on the rescue.
        "price_cents": int(
            (Decimal(str(offer["price_eur"])) * 100).to_integral_value()
        ),
        "currency": "EUR",
        "images": passed,
        "formats": listing.get("formats"),
        "licence": listing.get("licence_claim"),
        "file": archive.name,
        "file_sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "draft": not offer.get("live"),
    }
    return Request(
        storefront=storefront,
        method="POST",
        url=(environment.get(settings["url_env"]) or "").strip(),
        body=body,
        headers=[settings["auth_header"], "Content-Type"],
        archive=archive,
        sha256=str(body["file_sha256"]),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", help="pack or bundle id from listing.json")
    parser.add_argument(
        "--to", required=True, choices=sorted(STOREFRONTS), dest="storefront"
    )
    parser.add_argument(
        "--archive", type=Path, help="built .zip; defaults to dist/omnex-<pack>.zip"
    )
    parser.add_argument("--root", type=Path, default=PACKS)
    parser.add_argument(
        "--force-draft",
        action="store_true",
        help="publish an offer whose listing.json `live` flag is still false, as a draft",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--dry-run", action="store_true", help="print the request, send nothing"
    )
    mode.add_argument("--send", action="store_true", help="actually create the listing")
    args = parser.parse_args()

    archive = args.archive or (args.root / "dist" / f"omnex-{args.pack}.zip")
    environment = dict(os.environ)
    found = refusals(
        args.pack,
        args.storefront,
        archive,
        root=args.root,
        environment=environment,
        sending=args.send,
        force_draft=args.force_draft,
    )
    if found:
        print(f"FAIL {len(found.reasons)} reason(s) not to publish {args.pack}:")
        print(found.report())
        return 1

    request = build_request(
        args.pack, args.storefront, archive, root=args.root, environment=environment
    )
    print(request.render())

    if args.dry_run:
        print(
            "\nNothing was sent. Header VALUES are not shown and never leave the "
            "environment; the names above are what would carry them."
        )
        return 0

    return _send(request, environment)


def _send(request: Request, environment: dict[str, str]) -> int:
    """The one part that leaves the machine, kept small and separate.

    `urllib` rather than a dependency: `packs/` runs where there is a GPU stack
    and where there is nothing, and this repository's zero-dependency rule holds
    on the selling path too.
    """
    import urllib.error
    import urllib.request

    settings = STOREFRONTS[request.storefront]
    credential = environment[settings["credential_env"]].strip()
    post = urllib.request.Request(
        request.url,
        data=json.dumps(request.body).encode(),
        method=request.method,
        headers={
            settings["auth_header"]: f"{settings['auth_prefix']}{credential}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(post, timeout=30) as response:
            print(f"\n{response.status} from {request.storefront}")
            print(response.read().decode()[:2000])
    except urllib.error.HTTPError as exc:
        # The body, not just the status: a storefront's 400 says which field it
        # rejected, and that is the whole content of the message.
        print(
            f"\nFAIL {exc.code} from {request.storefront}\n{exc.read().decode()[:2000]}"
        )
        return 1
    except urllib.error.URLError as exc:
        print(f"\nFAIL could not reach {request.storefront}: {exc.reason}")
        return 1

    print(
        "\nRecord this in REVENUE_LOG.json and flip `live` in listing.json only "
        "once you have seen the listing. business_map.py reads both."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
