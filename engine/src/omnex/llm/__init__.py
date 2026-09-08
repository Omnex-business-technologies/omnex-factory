"""The model layer: one interface, several backings, exact cost on every call.

Everything downstream depends on `LanguageModel` and nothing else, which is what
makes a LiteLLM call, a local Ollama call and a scripted test double
interchangeable at every call site — and why the test suite needs no network.
"""

from .base import CallOptions, LanguageModel, compute_cost
from .catalog import CATALOG_PATH, ModelCatalog, ModelSpec, Tier
from .fakes import CapabilityModel, FlakyModel, ScriptedModel, SlowModel, Task, spec_for
from .tokens import HeuristicCounter, TiktokenCounter, TokenCounter
from .types import Completion, FinishReason, Message, Role, Usage

__all__ = [
    "CATALOG_PATH",
    "CallOptions",
    "CapabilityModel",
    "Completion",
    "FinishReason",
    "FlakyModel",
    "HeuristicCounter",
    "LanguageModel",
    "Message",
    "ModelCatalog",
    "ModelSpec",
    "Role",
    "ScriptedModel",
    "SlowModel",
    "Task",
    "Tier",
    "TiktokenCounter",
    "TokenCounter",
    "Usage",
    "compute_cost",
    "spec_for",
]
