PYTHON := $(shell which python3)
ENV := $(CURDIR)/env
PIP := $(ENV)/bin/pip
ENVPYTHON := $(ENV)/bin/python

default: help

help:
	@printf "\033[0;31mWelcome the the ex2rem Repo!\n"
	@grep -E '^[0-9a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo

$(ENV):
	virtualenv --python=$(PYTHON) $(ENV) --no-site-packages
	$(PIP) install -U pip setuptools

clean: ## cleans out the env
	rm -rf $(ENV)

deps: $(ENV) ## creates the virtualenv env
	$(PIP) install --upgrade -r requirements/base.txt

test: $(deps) ## tests the script, assumes a ex2rem.conf.test config file
	$(ENVPYTHON) ex2rem.py -c ex2rem.conf.test
