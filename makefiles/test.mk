##################
### Testing     ###
##################

.PHONY: test_unit
test_unit: ## Run unit tests
	$(call print_info_section,Running unit tests)
	$(Q).venv/bin/python -m pytest tests/ -v
	$(call print_success,Unit tests passed)

.PHONY: test_unit_coverage
test_unit_coverage: ## Run unit tests with coverage report
	$(call print_info_section,Running unit tests with coverage)
	$(Q)uv run pytest tests/ -v --cov=privy --cov-report=term-missing --cov-report=html
	$(call print_success,Coverage report generated at htmlcov/index.html)

.PHONY: test_watch
test_watch: ## Run tests in watch mode (requires pytest-watch)
	$(call print_info_section,Running tests in watch mode)
	$(Q)uv run ptw tests/ -- -v

.PHONY: test_specific
test_specific: ## Run specific test file (usage: make test_specific FILE=tests/test_import_wallet.py)
	$(call print_info_section,Running specific test: $(FILE))
	$(Q)uv run pytest $(FILE) -v
