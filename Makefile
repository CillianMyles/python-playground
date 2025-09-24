VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: setup-venv verify-venv install-deps destroy-venv lint lint-fix format

setup-venv:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip

verify-venv:
	which python
	which pip
	python -m pip --version

install-deps:
	$(PYTHON) -m pip install --pre mojo --index-url https://dl.modular.com/public/nightly/python/simple
	$(PYTHON) -m pip install -r requirements.txt

destroy-venv:
	rm -rf $(VENV)

lint:
	ruff check .

lint-fix:
	ruff check . --fix

format:
	ruff format .
