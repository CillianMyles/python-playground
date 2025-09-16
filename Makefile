VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: setup-venv verify-venv destroy-venv install-deps

setup-venv:
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip

verify-venv:
	which python
	which pip
	python -m pip --version

destroy-venv:
	rm -rf $(VENV)

install-deps:
	$(PYTHON) -m pip install --pre mojo --index-url https://dl.modular.com/public/nightly/python/simple
	$(PYTHON) -m pip install -r requirements.txt
