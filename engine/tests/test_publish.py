"""The last step before money, and the five things it refuses to do.

`listing_check.py` decides whether the goods cover the promise. `build_pack.py`
turns them into a file a buyer downloads. This is the request that creates the
listing, and every refusal in it is a way that listing could otherwise go up
taking money for something.

The request is built and never sent in these tests, which is not a limitation
here — it is the design. The storefront API shapes were not readable from the
environment this was written in, so no endpoint is written into the repository;
`--send` requires one from the operator's environment and refuses by name without
it. Everything that IS knowable — the refusals, the body, the price in integer
cents, which credential is used — is knowable offline and is checked here.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

REPO = Path(__file__).resolve().parents[2]
PACKS = REPO / "packs"
PUBLISH = PACKS / "publish.py"

pytestmark = pytest.mark.skipif(not PUBLISH.exists(), reason="packs/ is not in this checkout")


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location("packs_publish", PUBLISH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["packs_publish"] = module
    spec.loader.exec_module(module)
    return module


def _storefront(root: Path, *, live: bool = True, price: object = 19, images: int = 2) -> Path:
    """A pack whose goods cover its promise, so each refusal can be tested alone."""
    (root / "cosmetics" / "images").mkdir(parents=True, exist_ok=True)
    entries = [f"scene-{i:03}.png" for i in range(images)]
    for entry in entries:
        (root / "cosmetics" / "images" / entry).write_bytes(b"png")
    (root / "cosmetics" / "manifest.json").write_text(
        json.dumps({"pack": "cosmetics", "images": [{"file": e} for e in entries]}),
        encoding="utf-8",
    )
    offer: dict[str, object] = {
        "listing_name": "Luxury Cosmetics Scenes",
        "promised_images": images,
        "live": live,
    }
    if price is not None:
        offer["price_eur"] = price
    (root / "listing.json").write_text(
        json.dumps(
            {
                "version": "1",
                "formats": ["1:1", "4:5", "9:16", "16:9"],
                "licence_claim": "Full commercial licence, unlimited projects",
                "packs": {"cosmetics": offer},
            }
        ),
        encoding="utf-8",
    )
    archive = root / "dist" / "omnex-cosmetics.zip"
    archive.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("1x1/scene-000.png", b"bytes")
    return archive


def _reasons(module: ModuleType, root: Path, archive: Path | None, **kwargs: object) -> list[str]:
    return module.refusals(
        "cosmetics",
        "lemonsqueezy",
        archive,
        root=root,
        environment=kwargs.pop("environment", {"OMNEX_LEMONSQUEEZY_KEY": "k"}),
        **kwargs,
    ).reasons


# ── what it refuses ───────────────────────────────────────────────────────
def test_a_listing_the_goods_do_not_cover_is_refused(tmp_path: Path) -> None:
    """The €49 Vault sells 170 images against 80 through QC."""
    module = _module()
    archive = _storefront(tmp_path, images=2)
    listing = json.loads((tmp_path / "listing.json").read_text(encoding="utf-8"))
    listing["packs"]["cosmetics"]["promised_images"] = 50
    (tmp_path / "listing.json").write_text(json.dumps(listing), encoding="utf-8")

    reasons = _reasons(module, tmp_path, archive)
    assert any("promises more than QC passed" in r for r in reasons)
    assert any("goods nobody has" in r for r in reasons)


def test_a_missing_archive_is_refused(tmp_path: Path) -> None:
    """The file a buyer downloads must be the file that was checked."""
    module = _module()
    _storefront(tmp_path)
    reasons = _reasons(module, tmp_path, tmp_path / "dist" / "not-built.zip")
    assert any("no built archive" in r for r in reasons)


def test_an_offer_with_no_price_is_refused(tmp_path: Path) -> None:
    """A listing created at zero is a free pack sold as a paid one."""
    module = _module()
    archive = _storefront(tmp_path, price=None)
    assert any("no price" in r for r in _reasons(module, tmp_path, archive))


def test_an_unconfigured_credential_is_refused_before_anything_is_sent(tmp_path: Path) -> None:
    """Failing here is a message; failing at the storefront is a half-created listing."""
    module = _module()
    archive = _storefront(tmp_path)
    reasons = _reasons(module, tmp_path, archive, environment={})
    assert any("OMNEX_LEMONSQUEEZY_KEY is not set" in r for r in reasons)


def test_sending_with_no_endpoint_is_refused_by_name(tmp_path: Path) -> None:
    """No endpoint is written into this repository, and the refusal says which variable."""
    module = _module()
    archive = _storefront(tmp_path)
    assert _reasons(module, tmp_path, archive, sending=False) == []
    reasons = _reasons(module, tmp_path, archive, sending=True)
    assert any("OMNEX_LEMONSQUEEZY_URL is not set" in r for r in reasons)
    assert any("worse than a blank" in r for r in reasons)


def test_an_offer_that_is_not_live_needs_the_draft_flag(tmp_path: Path) -> None:
    """Going live starts the clock on `registry.ts`'s rule, and is a person's decision."""
    module = _module()
    archive = _storefront(tmp_path, live=False)
    assert any("live: false" in r for r in _reasons(module, tmp_path, archive))
    assert _reasons(module, tmp_path, archive, force_draft=True) == []


def test_an_unknown_pack_is_refused(tmp_path: Path) -> None:
    module = _module()
    _storefront(tmp_path)
    found = module.refusals("ghost", "lemonsqueezy", None, root=tmp_path, environment={})
    assert any("not an offer" in r for r in found.reasons)


def test_every_reason_is_reported_at_once(tmp_path: Path) -> None:
    """Being refused one at a time is how somebody concludes the check is the obstacle."""
    module = _module()
    _storefront(tmp_path, live=False, price=None)
    reasons = _reasons(
        module, tmp_path, tmp_path / "dist" / "gone.zip", environment={}, sending=True
    )
    assert len(reasons) >= 5, reasons


# ── what it builds ────────────────────────────────────────────────────────
def test_the_price_crosses_as_integer_cents(tmp_path: Path) -> None:
    """Every storefront prices in minor units, and a float here is the currency bug."""
    module = _module()
    archive = _storefront(tmp_path, price=19.99)
    body = module.build_request("cosmetics", "lemonsqueezy", archive, root=tmp_path).body
    assert body["price_cents"] == 1999
    assert isinstance(body["price_cents"], int)


def test_the_request_carries_the_hash_of_the_file_it_names(tmp_path: Path) -> None:
    """`build_pack.py` is deterministic so this is a hash rather than trust."""
    import hashlib

    module = _module()
    archive = _storefront(tmp_path)
    request = module.build_request("cosmetics", "lemonsqueezy", archive, root=tmp_path)
    assert request.sha256 == hashlib.sha256(archive.read_bytes()).hexdigest()
    assert request.body["file"] == archive.name


def test_the_body_reports_the_images_that_passed_and_not_the_promise(tmp_path: Path) -> None:
    """A listing describes the goods; the promise is what the goods are measured against."""
    module = _module()
    archive = _storefront(tmp_path, images=3)
    body = module.build_request("cosmetics", "lemonsqueezy", archive, root=tmp_path).body
    assert body["images"] == 3


def test_no_credential_reaches_the_request_or_its_rendering(tmp_path: Path) -> None:
    """The request is printed by --dry-run, and a printed key is a leaked key."""
    module = _module()
    archive = _storefront(tmp_path)
    secret = "lsq-live-DO-NOT-PRINT-ME"
    request = module.build_request(
        "cosmetics",
        "lemonsqueezy",
        archive,
        root=tmp_path,
        environment={
            "OMNEX_LEMONSQUEEZY_KEY": secret,
            "OMNEX_LEMONSQUEEZY_URL": "https://x.invalid",
        },
    )
    rendered = request.render()
    assert secret not in rendered
    assert secret not in json.dumps(request.body)
    assert request.headers == ["Authorization", "Content-Type"], "header names only, never values"
    assert request.url == "https://x.invalid", "the endpoint comes from the environment"


def test_no_endpoint_is_written_into_the_repository() -> None:
    """The rule the whole `--send` refusal exists to keep.

    A url from memory that imports cleanly and posts to the wrong host is worse
    than a blank, so there is not one anywhere in this file.
    """
    source = PUBLISH.read_text(encoding="utf-8")
    for storefront in ("lemonsqueezy.com", "etsy.com", "openapi.etsy"):
        assert storefront not in source, f"an endpoint for {storefront} was written down"


def test_both_storefronts_name_their_own_variables() -> None:
    module = _module()
    for name, settings in module.STOREFRONTS.items():
        assert settings["url_env"].startswith("OMNEX_"), name
        assert settings["credential_env"].startswith("OMNEX_"), name
        assert settings["url_env"] != settings["credential_env"]
