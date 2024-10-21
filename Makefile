# Makefile for python_tornado_object_storage
# https://www.gnu.org/software/make/manual/make.html
SHELL := /bin/sh
VENV = venv
VENV_BIN = ./$(VENV)/bin

install: requirements-ci.txt ## Install the application requirements
	# Use `python3` from the current environment to create a virtual environment
	python3 -m venv $(VENV)
	# Upgrade PIP in the virtual environment
	$(VENV_BIN)/python -m pip install --upgrade pip
	# Install the Python requirements in the virtual environment
	# CI requirements-ci.txt file includes dependencies for format, lint, and test
	$(VENV_BIN)/python -m pip install -r requirements-ci.txt

format: ## (Re)Format the application files
	$(VENV_BIN)/black *.py
	$(VENV_BIN)/black tests/*.py

lint: ## Lint the application files
	# Lint the application files
	$(VENV_BIN)/flake8 --max-line-length 127 *.py
	# Lint the test files
	$(VENV_BIN)/flake8 --max-line-length 127 tests/*.py

test: ## Test the application
	# Test the application
	$(VENV_BIN)/coverage run -m pytest -v tests/*.py
	# Report code coverage
	$(VENV_BIN)/coverage report -m

depcheck: ## Dependency check for known vulnarbilities
	# Perform a scan of dependancies backed by the OSS Index
	$(VENV_BIN)/jake --warn-only ddt

secscan: ## Run a source code security analyzer
	# Analyze the application files
	$(VENV_BIN)/bandit --recursive *.py

all: install lint test depcheck secscan

# Actions that don't require target files
.PHONY: clean
.PHONY: help

help: ## Print a list of make options available
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' ${MAKEFILE_LIST} | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

clean: ## Clean up files used locally when needed
	# Remove the Python cache files
	rm -rf ./__pycache__
	rm -rf ./tests/__pycache__
	# Remove the Python pytest files
	rm -rf ./.pytest_cache
	# Remove the Python the virtual environment
	rm -rf ./$(VENV)
