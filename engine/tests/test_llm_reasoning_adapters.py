"""The two adapters that must separate a reasoning model's <think> block.

No network here: `OllamaModel` is exercised against a monkeypatched
`urlopen`, and the LiteLLM adapter against a monkeypatched `litellm.completion`
-- consistent with the rest of this suite's `zero_required_dependencies`
invariant, and with how `test_core.py` already patches at the boundary rather
than mocking the objects under test.
"""

from __future__ import annotations

import json
import sys
import types
from typing import Any

import pytest

from omnex.llm import spec_for
from omnex.llm.base import CallOptions
from omnex.llm.catalog import Tier
from omnex.llm.litellm_adapter import LiteLlmModel
from omnex.llm.ollama import OllamaModel
from omnex.llm.types import Message


class _FakeHttpResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._body = json.dumps(payload).encode()

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> _FakeHttpResponse:
        return self

    def __exit__(self, *exc: object) -> bool:
        return False


def _patch_ollama_response(monkeypatch: pytest.MonkeyPatch, payload: dict[str, Any]) -> None:
    import omnex.llm.ollama as ollama_module

    monkeypatch.setattr(
        ollama_module.urllib.request, "urlopen", lambda *a, **k: _FakeHttpResponse(payload)
    )


def test_ollama_uses_the_separate_thinking_field_when_the_daemon_provides_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Newer Ollama versions already separate reasoning -- do not re-parse it."""
    _patch_ollama_response(
        monkeypatch,
        {
            "message": {"content": "Paris.", "thinking": "The user wants the capital."},
            "prompt_eval_count": 10,
            "eval_count": 5,
        },
    )
    model = OllamaModel(spec_for("r1", Tier.REASONING, "0", "0"))
    completion = model.complete([Message("user", "capital of France?")], CallOptions())

    assert completion.text == "Paris."
    assert completion.reasoning == "The user wants the capital."
    assert completion.reasoned


def test_ollama_falls_back_to_tag_splitting_when_no_thinking_field_is_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_ollama_response(
        monkeypatch,
        {
            "message": {"content": "<think>reasoning here</think>Paris."},
            "prompt_eval_count": 10,
            "eval_count": 5,
        },
    )
    model = OllamaModel(spec_for("r1", Tier.REASONING, "0", "0"))
    completion = model.complete([Message("user", "capital of France?")], CallOptions())

    assert completion.text == "Paris."
    assert completion.reasoning == "reasoning here"


def test_ollama_with_neither_shape_leaves_reasoning_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    _patch_ollama_response(
        monkeypatch,
        {"message": {"content": "Paris."}, "prompt_eval_count": 10, "eval_count": 5},
    )
    model = OllamaModel(spec_for("plain", Tier.NANO, "0", "0"))
    completion = model.complete([Message("user", "capital of France?")], CallOptions())

    assert completion.text == "Paris."
    assert completion.reasoning == ""
    assert not completion.reasoned


class _FakeUsage:
    def __init__(self, prompt_tokens: int, completion_tokens: int) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens


class _FakeMessage:
    def __init__(self, content: str, reasoning_content: str = "") -> None:
        self.content = content
        if reasoning_content:
            self.reasoning_content = reasoning_content


class _FakeChoice:
    def __init__(self, message: _FakeMessage, finish_reason: str = "stop") -> None:
        self.message = message
        self.finish_reason = finish_reason


class _FakeLiteLLMResponse:
    def __init__(self, choice: _FakeChoice, usage: _FakeUsage) -> None:
        self.choices = [choice]
        self.usage = usage


def _adapter(monkeypatch: pytest.MonkeyPatch, response: _FakeLiteLLMResponse) -> LiteLlmModel:
    """`litellm` is imported lazily inside `complete()` (never a required
    dependency), so it is faked at `sys.modules` rather than as a module
    attribute -- there is no real `litellm` installed in this environment for
    `monkeypatch.setattr` to find."""
    fake = types.ModuleType("litellm")
    fake.completion = lambda **kw: response  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "litellm", fake)
    return LiteLlmModel(spec_for("gpt-x", Tier.REASONING, "3.00", "15.00"))


def test_litellm_uses_the_providers_own_reasoning_content_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = _FakeLiteLLMResponse(
        _FakeChoice(_FakeMessage("Paris.", reasoning_content="thinking about capitals")),
        _FakeUsage(10, 5),
    )
    completion = _adapter(monkeypatch, response).complete(
        [Message("user", "capital of France?")], CallOptions()
    )
    assert completion.text == "Paris."
    assert completion.reasoning == "thinking about capitals"


def test_litellm_falls_back_to_tag_splitting_when_no_reasoning_content_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = _FakeLiteLLMResponse(
        _FakeChoice(_FakeMessage("<think>inline thinking</think>Paris.")), _FakeUsage(10, 5)
    )
    completion = _adapter(monkeypatch, response).complete(
        [Message("user", "capital of France?")], CallOptions()
    )
    assert completion.text == "Paris."
    assert completion.reasoning == "inline thinking"
