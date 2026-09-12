"""`n8n_bindings_check.py` — a real checker with real defects behind it and,
until now, no test of its own.

The module's own docstring names the exact failure this exists to catch: two
bindings once named `python -m omnex.pipeline.verify_webhook` and
`...seen_before`, neither of which was a module, and every schema-level check
already written passed both. Nothing here duplicates `bindings.load()`'s own
tests (`test_factory_compile.py` or similar) — this only exercises what
`n8n_bindings_check.py` itself adds: command resolution and the environment
variable derivation, plus a test that the committed catalogue this repository
actually ships still resolves cleanly.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1]
REPO = ENGINE.parent
sys.path.insert(0, str(ENGINE / "scripts"))
sys.path.insert(0, str(ENGINE / "src"))

import n8n_bindings_check  # noqa: E402

from omnex.factory.compile import bindings  # noqa: E402

_NODE_TYPES = {
    "http": {"type": "n8n-nodes-base.httpRequest", "type_version": 1},
    "exec": {"type": "n8n-nodes-base.executeCommand", "type_version": 1},
}


def _write(raw: dict[str, object], tmp_path: Path) -> Path:
    target = tmp_path / "catalogue.json"
    target.write_text(json.dumps(raw), encoding="utf-8")
    return target


def test_a_module_with_no_main_is_reported_unresolved(tmp_path: Path) -> None:
    """The exact defect the module's docstring names: a command naming a
    package that has no __main__, so `python -m <it>` cannot run."""
    catalogue = bindings.load(
        _write(
            {
                "node_types": _NODE_TYPES,
                "bindings": {
                    "order.deduplicate": {
                        "node_type": "exec",
                        "source": "this repository",
                        "parameters": {"command": "python -m omnex.pipeline.verify_webhook"},
                    }
                },
            },
            tmp_path,
        )
    )
    problems = n8n_bindings_check.unresolved_commands(catalogue)
    assert len(problems) == 1
    assert "has no __main__" in problems[0]


def test_a_real_module_and_subcommand_resolves(tmp_path: Path) -> None:
    catalogue = bindings.load(
        _write(
            {
                "node_types": _NODE_TYPES,
                "bindings": {
                    "order.verify": {
                        "node_type": "exec",
                        "source": "this repository",
                        "parameters": {"command": "python -m omnex.pipeline verify"},
                    }
                },
            },
            tmp_path,
        )
    )
    assert n8n_bindings_check.unresolved_commands(catalogue) == []


def test_a_real_module_with_a_bad_subcommand_is_reported(tmp_path: Path) -> None:
    catalogue = bindings.load(
        _write(
            {
                "node_types": _NODE_TYPES,
                "bindings": {
                    "order.verify": {
                        "node_type": "exec",
                        "source": "this repository",
                        "parameters": {
                            "command": "python -m omnex.pipeline nonexistent_subcommand"
                        },
                    }
                },
            },
            tmp_path,
        )
    )
    problems = n8n_bindings_check.unresolved_commands(catalogue)
    assert len(problems) == 1
    assert "is not a subcommand" in problems[0]


def test_a_binding_that_names_no_command_is_reported(tmp_path: Path) -> None:
    catalogue = bindings.load(
        _write(
            {
                "node_types": _NODE_TYPES,
                "bindings": {
                    "order.mystery": {
                        "node_type": "exec",
                        "source": "this repository",
                        "parameters": {},
                    }
                },
            },
            tmp_path,
        )
    )
    problems = n8n_bindings_check.unresolved_commands(catalogue)
    assert len(problems) == 1
    assert "names no command" in problems[0]


def test_a_proposal_sourced_binding_is_never_checked(tmp_path: Path) -> None:
    """A storefront endpoint's command cannot be resolved from here, and
    `unresolved_commands` must not try — only `source: this repository`
    entries claim to be checkable at all."""
    catalogue = bindings.load(
        _write(
            {
                "node_types": _NODE_TYPES,
                "bindings": {
                    "etsy.create": {
                        "node_type": "http",
                        "source": "proposal",
                        "parameters": {"command": "curl totally-not-a-module"},
                    }
                },
            },
            tmp_path,
        )
    )
    assert n8n_bindings_check.unresolved_commands(catalogue) == []


def test_required_env_reads_interpolated_and_declared_variables(tmp_path: Path) -> None:
    catalogue = bindings.load(
        _write(
            {
                "node_types": _NODE_TYPES,
                "bindings": {
                    "order.verify": {
                        "node_type": "exec",
                        "source": "this repository",
                        "parameters": {
                            "command": "python -m omnex.pipeline verify --sig $OMNEX_SIGNATURE"
                        },
                        "env": ["OMNEX_WEBHOOK_SECRET"],
                    }
                },
            },
            tmp_path,
        )
    )
    env = n8n_bindings_check.required_env(catalogue)
    assert env == {
        "OMNEX_SIGNATURE": ["order.verify"],
        "OMNEX_WEBHOOK_SECRET": ["order.verify"],
    }


def test_main_fails_when_the_catalogue_will_not_load(tmp_path: Path, monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    broken = _write(
        {"node_types": _NODE_TYPES, "bindings": {"thing.do": {"node_type": "does_not_exist"}}},
        tmp_path,
    )
    monkeypatch.setattr(n8n_bindings_check, "CATALOGUE", broken)
    assert n8n_bindings_check.main() == 1
    assert "FAIL" in capsys.readouterr().out


def test_main_fails_on_an_unresolved_command(tmp_path: Path, monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    catalogue_path = _write(
        {
            "node_types": _NODE_TYPES,
            "bindings": {
                "order.deduplicate": {
                    "node_type": "exec",
                    "source": "this repository",
                    "parameters": {"command": "python -m omnex.pipeline.verify_webhook"},
                }
            },
        },
        tmp_path,
    )
    monkeypatch.setattr(n8n_bindings_check, "CATALOGUE", catalogue_path)
    assert n8n_bindings_check.main() == 1
    assert "FAIL" in capsys.readouterr().out


def test_the_committed_catalogue_resolves_cleanly() -> None:
    """The whole point: this repository's real n8n_bindings.json, checked as
    CI would check it -- until this test existed, nothing did."""
    catalogue = bindings.load(n8n_bindings_check.CATALOGUE)
    assert n8n_bindings_check.unresolved_commands(catalogue) == []
