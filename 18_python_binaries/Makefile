VENV := ../.venv
PYTHON := $(VENV)/bin/python
TARGET := ../15_compare_csv_files/main.py

.PHONY: create-pyinstaller
create-pyinstaller:
	@echo "==> Building PyInstaller binary..."
	@/usr/bin/time -p $(PYTHON) -m pyinstaller \
		--noconfirm \
		--clean \
		--onefile \
		--name main \
		--distpath dist_pyinstaller \
		--workpath build_pyinstaller \
		--specpath spec_pyinstaller \
		$(TARGET)

.PHONY: create-nuitka
create-nuitka:
	@echo "==> Building Nuitka binary..."
	@/usr/bin/time -p $(PYTHON) -m nuitka \
		--onefile \
		--assume-yes-for-downloads \
		--output-dir=dist_nuitka \
		--output-filename=main \
		$(TARGET)

.PHONY: verify-pyinstaller
verify-pyinstaller:
	@echo "==> Verifying PyInstaller binary..."
	@/usr/bin/time -p ./dist_pyinstaller/main -h

.PHONY: verify-nuitka
verify-nuitka:
	@echo "==> Verifying Nuitka binary..."
	@/usr/bin/time -p ./dist_nuitka/main -h
