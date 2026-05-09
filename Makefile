# CAE — Cold Forge. Every command runs INSIDE the container.
SHELL := /bin/bash
IMAGE := cae-research-kit:0.1.0
SEED  ?= 42

DOCKER_RUN := docker run --rm \
    -e PYTHONHASHSEED=$(SEED) \
    -e CAE_SEED=$(SEED) \
    -v $(CURDIR)/research:/workspace/research \
    -v $(CURDIR)/tests:/workspace/tests:ro \
    -v $(CURDIR)/src:/workspace/src:ro \
    $(IMAGE)

.PHONY: build bootstrap-check adt test shell clean refuse-host

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
