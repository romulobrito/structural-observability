PYTHON ?= python3

.PHONY: install install-app test test-all run-cases min-inst app

install:
	$(PYTHON) -m pip install -e .

install-app:
	$(PYTHON) -m pip install -e ".[app]"

test:
	$(PYTHON) tests/test_tearing_semantics.py
	$(PYTHON) tests/test_urs_pdf_regression.py

test-all: test
	$(PYTHON) -m pytest tests/ -q

run-cases:
	structural-obs-run-cases --case 01_urs_ideal --case 02_urs_real

min-inst:
	structural-obs-min-inst --mode repair

app:
	structural-obs-app
