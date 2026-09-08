# The engine, with only its dev dependencies — built from the repository
# root, not engine/ alone.
#
# It was engine/ alone until D-012. The first time anything ever built this
# image, the baked test run failed: ~90 of the engine's own tests read
# lib/, oss/, corpus/, state/, .github/workflows/, CLAUDE.md and
# execution_state.json by design (CLAUDE.md's own engine.yml comment already
# says so), and Path(__file__).resolve().parents[2] — the idiom nearly every
# one of them uses to find the repository root — resolved to the filesystem
# root instead, because none of that tree was ever copied in. A context of
# engine/ alone could never have supplied it.
#
# No CUDA base image, no torch, no model weights: the local tier runs
# inference in the Ollama container next door, and this one only needs to be
# able to run the engine and its actual test suite. .dockerignore at the
# repository root keeps the copy from also including node_modules/, .next/
# and .git/ — by far the three heaviest directories here — so this still
# lands far closer to "a stack someone tries" than "one they abandon at the
# download," even though the exact number that comparison names was never
# measured against a full-repo context and is not repeated here.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /repo
COPY . .

WORKDIR /repo/engine
RUN pip install --no-cache-dir -e '.[dev]'

# Fails the build if the suite needs a credential — the property the whole
# local tier depends on, checked at image build rather than assumed. Runs
# from the repo root now, so the tests that read outside engine/ can.
RUN python -m pytest tests/ -q

CMD ["python", "-m", "pytest", "tests/", "-q"]
