# CAE — Cold Forge. Every command runs INSIDE the container.
SHELL := /bin/bash
IMAGE := cae-research-kit:0.7.0
SEED  ?= 42

DOCKER_RUN := docker run --rm \
    -e PYTHONHASHSEED=$(SEED) \
    -e CAE_SEED=$(SEED) \
    -v $(CURDIR)/research:/workspace/research \
    -v $(CURDIR)/tests:/workspace/tests:ro \
    -v $(CURDIR)/src:/workspace/src:ro \
    $(IMAGE)

# CAE-Cert v0.1 host runs (ADR-036): keys live OUTSIDE the container.
# These targets do NOT use docker — issuance must occur on the issuer's
# host where ~/.cae-keys/ is readable. Verification is host-only too,
# but only requires the public key shipped in the repo.
CERT_KEYDIR  ?= $(HOME)/.cae-keys
CERT_PRIV    ?= $(CERT_KEYDIR)/cae-cert-issuer.ed25519
CERT_PUB_REPO := keys/cae-cert-issuer.pub

.PHONY: build bootstrap-check adt test shell clean refuse-host \
        keygen-cert issue-cert-v060 verify-cert-v060 cert-tests

build:
	docker build --pull -t $(IMAGE) .

bootstrap-check: build
	$(DOCKER_RUN) python -m src.config.determinism

adt: build
	$(DOCKER_RUN) python -m pytest tests/adt -q

test: adt

shell: build
	$(DOCKER_RUN) bash

# ADT-C4 safety net: host executions explicitly refused.
refuse-host:
	@echo "[CAE] Host execution forbidden. Use 'make adt' (container)." && exit 2

clean:
	-docker image rm $(IMAGE) 2>/dev/null || true
	rm -rf __pycache__ .pytest_cache **/__pycache__ *.egg-info

# ----------------------------------------------------------------------
# CAE-Cert v0.1 — ADR-036
# ----------------------------------------------------------------------
keygen-cert:
	mkdir -p $(CERT_KEYDIR) keys
	PYTHONPATH=. python -m src.cert.keygen \
	    --output-private $(CERT_PRIV) \
	    --output-public  $(CERT_KEYDIR)/cae-cert-issuer.pub
	cp $(CERT_KEYDIR)/cae-cert-issuer.pub $(CERT_PUB_REPO)
	@echo "[CAE-Cert] Public key copied to $(CERT_PUB_REPO)."
	@echo "[CAE-Cert] Private key kept under $(CERT_PRIV) (chmod 600)."

issue-cert-v060:
	PYTHONPATH=. python scripts/issue_v060_cert.py

verify-cert-v060:
	PYTHONPATH=. python -m src.cert.verify \
	    --cert research/cae-cert-v0.6.0.v01.json \
	    --sig  research/cae-cert-v0.6.0.v01.json.sig \
	    --public-key $(CERT_PUB_REPO) \
	    --repo-root .

cert-tests:
	PYTHONPATH=. python -m pytest tests/cert -v
