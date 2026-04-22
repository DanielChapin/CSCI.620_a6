PY=python3
VENV=.venv
USE_VENV=source $(VENV)/bin/activate

SHELL := /bin/bash

.DEFAULT_GOAL := $(VENV)

.PHONY: $(VENV)
$(VENV):
	$(PY) -m venv $(VENV)
	$(USE_VENV) && pip install -r requirements.txt

.PHONY: requirements.txt
requirements.txt:
	$(USE_VENV) && pip freeze > requirements.txt

out/a6-dsc4984.zip: Makefile src/*.py src/sql/*.sql .env.sample README.md requirements.txt report/dsc4984_a6.pdf
	mkdir -p out
	zip $@ $^
