VENV := ../.venv
PYTHON := $(VENV)/bin/python
TARGET := ../15_compare_csv_files/main.py

.PHONY: pyinstaller
pyinstaller:
	$(PYTHON) -m pyinstaller --noconfirm --clean --onefile --name main --distpath dist_pyinstaller --workpath build_pyinstaller --specpath spec_pyinstaller $(TARGET)

.PHONY: nuitka
nuitka:
	$(PYTHON) -m nuitka --onefile --assume-yes-for-downloads --output-dir=dist_nuitka --output-filename=main $(TARGET)
