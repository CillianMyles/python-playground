.PHONY: test-python test-mojo

test-python:
	python -m pytest -q tests/test_soundex.py

test-mojo:
	mojo test -I src tests/test_soundex.mojo
