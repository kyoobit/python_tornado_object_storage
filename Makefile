# Makefile for python_tornado_object_storage
# https://www.gnu.org/software/make/manual/make.html
SHELL := /bin/sh

# Actions that don't require target files
.PHONY: install install-dev format lint test depcheck secscan all clean help

install: pyproject.toml uv.lock ## Install the application requirements
	# Set the python version in `.python-version'
	# Report the `uv' version or install `uv' when missing
	uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh
	# Install the Python requirements using `uv' in the virtual environment
	# Use --frozen for the exact version used in the uv.lock file
	uv sync --frozen

install-dev: pyproject.toml uv.lock ## Install the application requirements
	# Set the python version in `.python-version'
	# Report the `uv' version or install `uv' when missing
	uv --version || curl -LsSf https://astral.sh/uv/install.sh | sh
	# Install the Python requirements using `uv' in the virtual environment
	# Include the development dependencies used for additional CI/CD checks
	# Upgrade as packages become available (Use --frozen for the exact version)
	uv sync --all-extras --dev --upgrade

format: ## (Re)Format the application files
	# (Re)Format the application files
	uv run ruff format .

lint: ## Lint the application files
	# (Use --fix to automatically fix issues where possible)
	uv run ruff check .

test: ## Test the application
	# Test the application
	uv run coverage run -m pytest -v tests/*.py
	# Report code coverage
	uv run coverage report -m
	# Use `coverage html' to generate a HTML coverage report

depcheck: ## Dependency check for known vulnerabilities
	# Perform a scan of dependencies using uv
	# https://docs.astral.sh/uv/reference/cli/#uv-audit
	uv audit --verbose --no-cache

secscan: ## Run a source code security analyzer
	# Analyze the application files
	# Ignore B101 Use of assert detected, due to laziness of putting tests in the same file
	uv run bandit --recursive *.py

all: install-dev format lint test depcheck secscan ## Run all checks

help: ## Print a list of make options available
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' ${MAKEFILE_LIST} | sort | \
	awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

clean: ## Clean up files used locally when needed
	# Remove all Python cache files recursively
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete 2>/dev/null || true
	find . -type f -name '*.pyo' -delete 2>/dev/null || true
	# Remove Python pytest files
	rm -rf ./.pytest_cache
	# Remove coverage files
	rm -rf ./.coverage htmlcov/ .coverage.*
	# Remove build artifacts
	rm -rf ./build ./dist ./*.egg-info
	# Remove the Python virtual environment
	rm -rf ./.venv
	# Remove uv cache (optional)
	# uv cache clean
