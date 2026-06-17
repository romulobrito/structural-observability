PYTHON ?= python3

.PHONY: install test test-all run-cases min-inst

install:
	$(PYTHON) -m pip install -e .

test:
	$(PYTHON) tests/test_tearing_semantics.py
	$(PYTHON) tests/test_urs_pdf_regression.py

test-all: test

run-cases:
	structural-obs-run-cases --case 01_urs_ideal --case 02_urs_real

min-inst:
	structural-obs-min-inst --mode repair
