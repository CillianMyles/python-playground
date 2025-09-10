PYTHON ?= python3

.PHONY: install-deps
install-deps:
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install $$(pipx run toml-cli get pyproject.toml project.dependencies | awk -F'=' '{print $$1}')
