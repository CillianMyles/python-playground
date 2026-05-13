VENV := .venv
PYTHON := $(VENV)/bin/python
PIP_INDEX_URL := https://pypi.org/simple
PIP_ENV := PIP_INDEX_URL=$(PIP_INDEX_URL) PIP_EXTRA_INDEX_URL=
PIP_ARGS := --index-url $(PIP_INDEX_URL)

.PHONY: setup-venv
setup-venv:
	python3 -m venv $(VENV)
	$(PIP_ENV) $(PYTHON) -m pip install $(PIP_ARGS) --upgrade pip

.PHONY: verify-venv
verify-venv:
	which python
	which pip
	python -m pip --version
	@echo "PIP_INDEX_URL=$$PIP_INDEX_URL"
	@echo "PIP_EXTRA_INDEX_URL=$$PIP_EXTRA_INDEX_URL"
	$(PIP_ENV) $(PYTHON) -m pip config list

.PHONY: install-deps
install-deps:
	$(PIP_ENV) $(PYTHON) -m pip install $(PIP_ARGS) -r requirements.txt

.PHONY: destroy-venv
destroy-venv:
	rm -rf $(VENV)

.PHONY: lint
lint:
	ruff check .

.PHONY: lint-fix
lint-fix:
	ruff check . --fix

.PHONY: format
format:
	ruff format .
