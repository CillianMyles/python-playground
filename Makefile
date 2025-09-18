VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: setup-venv
setup-venv:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip

.PHONY: verify-venv
verify-venv:
	which python
	which pip
	python -m pip --version

.PHONY: install-deps
destroy-venv:
	rm -rf $(VENV)

.PHONY: install-deps
install-deps:
	$(PYTHON) -m pip install --pre mojo --index-url https://dl.modular.com/public/nightly/python/simple
	$(PYTHON) -m pip install -r requirements.txt

.PHONY: lint
lint:
	ruff check .

.PHONY: lint-fix
lint-fix:
	ruff check . --fix

.PHONY: format
format:
	ruff format .
