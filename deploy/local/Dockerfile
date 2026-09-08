# The engine, with only its dev dependencies.
#
# No CUDA base image, no torch, no model weights: the local tier runs inference
# in the Ollama container next door, and this one only needs to be able to run
# the engine and its tests. The result is ~120 MB instead of ~8 GB, which is the
# difference between a stack someone tries and one they abandon at the download.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src

RUN pip install --no-cache-dir -e '.[dev]'

COPY . .

# Fails the build if the suite needs a credential — the property the whole
# local tier depends on, checked at image build rather than assumed.
RUN python -m pytest tests/ -q

CMD ["python", "-m", "pytest", "tests/", "-q"]
