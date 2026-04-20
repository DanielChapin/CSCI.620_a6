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

out/a2-dsc4984.zip: Makefile src/*.py src/sql/*.sql .env.sample get_dataset.sh README.md requirements.txt
	mkdir -p out
	zip $@ $^
