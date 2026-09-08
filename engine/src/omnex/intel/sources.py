"""Source adapters — where evidence comes from, and what each source can prove.

## The network reality this was built against, stated rather than discovered later

From inside this execution environment the outbound proxy permits some hosts and
refuses others. Measured, not assumed:

    reachable   PyPI · npm · crates.io · GitLab · Docker Hub
    blocked     GitHub · Hugging Face · arXiv · HN Algolia   (403 at the proxy)

That is not a defect to work around silently. It shapes the design: adapters
exist for the hosts that answer, and everything else enters through the committed
`EvidenceFile`, fetched out of band by whatever has credentials — an operator, a
CI job, an agent with a browser tool. `report.py` reads only the evidence file,
so a report regenerates identically on a machine with no network at all.

## Why package registries are the better signal anyway

Stars measure attention: who saw a link and approved of it. Registry downloads
measure adoption: whose build actually pulls the thing every week. The two
diverge constantly, and the gap is itself intelligence — a project with 8,000
stars and no distribution is a well-marketed README, and a library with 300 stars
inside a million weekly installs is infrastructure somebody already depends on.

`requires_dist` and npm `dependencies` are better still. A dependency list is the
architecture, declared by the author, in machine-readable form: a package
depending on `fastapi`, `celery` and `redis` has told you its service topology
more reliably than its own documentation will. `reverse.py` reads them for
exactly that.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from ..core.clock import Clock, SystemClock
from .evidence import MAX_EXCERPT_CHARS, Artifact, Confidence, Evidence

__all__ = [
    "BLOCKED_HOSTS",
    "CratesSource",
    "DockerHubSource",
    "NpmSource",
    "PypiSource",
    "Source",
    "SourceUnavailable",
    "fetch_all",
]

#: Documented so a caller knows why an adapter is absent rather than assuming
#: one was forgotten. Verified by probe, 2026-08-05.
BLOCKED_HOSTS = ("github.com", "huggingface.co", "export.arxiv.org", "hn.algolia.com")


class SourceUnavailable(Exception):
    """The host refused or the identifier does not exist. Never fatal to a scan."""


@runtime_checkable
class Source(Protocol):
    """One place public projects can be looked up.

    Adding a registry is one class. Nothing above this module knows which
    registry an `Artifact` came from except through its `source` field.
    """

    name: str

    def fetch(self, identifier: str) -> Artifact: ...


def _get_json(url: str, timeout: float = 15.0) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": "omnex-intel/0.1"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise SourceUnavailable(f"{url} returned {exc.code}") from exc
    except (OSError, json.JSONDecodeError) as exc:
        raise SourceUnavailable(f"{url}: {exc}") from exc
    if not isinstance(payload, dict):
        raise SourceUnavailable(f"{url} returned {type(payload).__name__}, expected an object")
    return payload


def _excerpt(text: str) -> str:
    """Trim to the licence-safe limit at a word boundary."""
    clean = " ".join(str(text or "").split())
    if len(clean) <= MAX_EXCERPT_CHARS:
        return clean
    return clean[: MAX_EXCERPT_CHARS - 1].rsplit(" ", 1)[0] + "…"


@dataclass
class PypiSource:
    """PyPI. Gives licence, summary and — the valuable part — `requires_dist`."""

    name: str = "pypi"
    clock: Clock = field(default_factory=SystemClock)

    def fetch(self, identifier: str) -> Artifact:
        url = f"https://pypi.org/pypi/{identifier}/json"
        payload = _get_json(url)
        info = payload.get("info", {})
        if not isinstance(info, dict):
            raise SourceUnavailable(f"{url}: no info block")

        requires = info.get("requires_dist") or []
        dependencies = [str(item).split()[0].split("[")[0] for item in requires if item]
        page = f"https://pypi.org/project/{identifier}/"
        today = self.clock.now().date()

        return Artifact(
            id=f"pypi:{identifier}",
            name=identifier,
            source=self.name,
            url=page,
            description=_excerpt(info.get("summary", "")),
            language="Python",
            licence=str(info.get("license") or _licence_from_classifiers(info)),
            popularity=0,
            popularity_kind="downloads",
            tags=tuple(dependencies[:40]),
            corpus=_excerpt(info.get("summary", "")),
            evidence=(
                Evidence(
                    url=page,
                    fetched_on=today,
                    excerpt=_excerpt(info.get("summary", "")),
                    # The registry is authoritative about its own metadata.
                    confidence=Confidence.HIGH,
                ),
            ),
        )


def _licence_from_classifiers(info: dict[str, Any]) -> str:
    for classifier in info.get("classifiers", []) or []:
        text = str(classifier)
        if text.startswith("License :: OSI Approved :: "):
            return text.rsplit("::", 1)[-1].strip()
    return ""


@dataclass
class NpmSource:
    """npm. `dependencies` on the latest version is the declared architecture."""

    name: str = "npm"
    clock: Clock = field(default_factory=SystemClock)

    def fetch(self, identifier: str) -> Artifact:
        url = f"https://registry.npmjs.org/{identifier}"
        payload = _get_json(url)
        tags = payload.get("dist-tags", {})
        latest = tags.get("latest", "") if isinstance(tags, dict) else ""
        versions = payload.get("versions", {})
        manifest = versions.get(latest, {}) if isinstance(versions, dict) else {}
        if not isinstance(manifest, dict):
            manifest = {}

        deps = manifest.get("dependencies", {})
        dependencies = sorted(deps) if isinstance(deps, dict) else []
        page = f"https://www.npmjs.com/package/{identifier}"
        today = self.clock.now().date()
        description = _excerpt(payload.get("description", ""))

        return Artifact(
            id=f"npm:{identifier}",
            name=identifier,
            source=self.name,
            url=page,
            description=description,
            language="JavaScript/TypeScript",
            licence=str(payload.get("license") or manifest.get("license") or ""),
            popularity=0,
            popularity_kind="downloads",
            tags=tuple(dependencies[:40]),
            corpus=description,
            evidence=(
                Evidence(
                    url=page, fetched_on=today, excerpt=description, confidence=Confidence.HIGH
                ),
            ),
        )


@dataclass
class CratesSource:
    """crates.io. Reports real download counts, which stars never do."""

    name: str = "crates"
    clock: Clock = field(default_factory=SystemClock)

    def fetch(self, identifier: str) -> Artifact:
        url = f"https://crates.io/api/v1/crates/{identifier}"
        payload = _get_json(url)
        crate = payload.get("crate", {})
        if not isinstance(crate, dict):
            raise SourceUnavailable(f"{url}: no crate block")
        page = f"https://crates.io/crates/{identifier}"
        today = self.clock.now().date()
        description = _excerpt(crate.get("description", ""))

        return Artifact(
            id=f"crates:{identifier}",
            name=identifier,
            source=self.name,
            url=page,
            description=description,
            language="Rust",
            licence=str(crate.get("license") or ""),
            popularity=int(crate.get("downloads") or 0),
            popularity_kind="downloads",
            corpus=description,
            evidence=(
                Evidence(
                    url=page, fetched_on=today, excerpt=description, confidence=Confidence.HIGH
                ),
            ),
        )


@dataclass
class DockerHubSource:
    """Docker Hub. Pull counts are the closest public proxy for production use."""

    name: str = "dockerhub"
    clock: Clock = field(default_factory=SystemClock)

    def fetch(self, identifier: str) -> Artifact:
        namespace, _, repository = identifier.partition("/")
        if not repository:
            namespace, repository = "library", namespace
        url = f"https://hub.docker.com/v2/repositories/{namespace}/{repository}/"
        payload = _get_json(url)
        page = f"https://hub.docker.com/r/{namespace}/{repository}"
        today = self.clock.now().date()
        description = _excerpt(payload.get("description", ""))

        return Artifact(
            id=f"dockerhub:{namespace}/{repository}",
            name=f"{namespace}/{repository}",
            source=self.name,
            url=page,
            description=description,
            licence="",
            popularity=int(payload.get("pull_count") or 0),
            popularity_kind="pulls",
            corpus=_excerpt(
                f"{payload.get('description', '')} {payload.get('full_description', '')}"
            ),
            evidence=(
                Evidence(
                    url=page, fetched_on=today, excerpt=description, confidence=Confidence.HIGH
                ),
            ),
        )


def fetch_all(
    source: Source, identifiers: list[str], clock: Clock | None = None
) -> tuple[list[Artifact], list[tuple[str, str]]]:
    """Fetch many, and return the failures rather than raising on the first one.

    A scan that dies because one package was renamed has thrown away the other
    ninety-nine fetches. Failures are returned as `(identifier, reason)` so they
    appear in the report — a source that quietly returned nothing looks exactly
    like a source with nothing to report, and those need to be distinguishable.
    """
    _ = clock
    found: list[Artifact] = []
    failed: list[tuple[str, str]] = []
    for identifier in identifiers:
        try:
            found.append(source.fetch(identifier))
        except SourceUnavailable as exc:
            failed.append((identifier, str(exc)))
    return found, failed
