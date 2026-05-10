# CAE — Cold Forge
# Reproducible image for H5 instrumentation.
# No install outside pyproject.toml. No apt beyond what scipy/POT require.

FROM python:3.11.9-slim-bookworm

# --- Discipline variables (ADR-020) -------------------------------------------
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONHASHSEED=42 \
    CAE_SEED=42 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1

# --- Minimal tools for scientific wheels --------------------------------------
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# --- Pinned dependency layer (stable Docker cache) ----------------------------
COPY pyproject.toml ./
RUN pip install --upgrade "pip==24.0" "setuptools==69.5.1" "wheel==0.43.0" \
 && pip install \
        "numpy==1.26.4" \
        "scipy==1.12.0" \
        "POT==0.9.3" \
        "pandas==2.2.1" \
        "matplotlib==3.8.3" \
        "pytest==8.1.1" \
        "cryptography>=42,<43" \
        "jcs==0.2.1" \
        "PyYAML>=6,<7"

# --- Application code ---------------------------------------------------------
COPY . .

# Prevent pytest from writing to non-instrumented paths
ENV PYTEST_ADDOPTS="-q --color=no"

# Sanity check baked into the image (build fails if determinism is broken)
RUN PYTHONHASHSEED=42 python -m src.config.determinism

CMD ["python", "-m", "pytest", "tests/adt", "-q"]
