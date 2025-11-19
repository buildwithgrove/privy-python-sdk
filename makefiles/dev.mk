####################
### Development   ###
####################

.PHONY: dev_quality_format
dev_quality_format: ## Format and lint code (black, isort, ruff)
	$(call print_info_section,Formatting and linting code)
	@printf "$(BOLD)Formatting with black...$(RESET)\n"
	$(Q)uv run black privy/ tests/
	@printf "$(BOLD)Sorting imports with isort...$(RESET)\n"
	$(Q)uv run isort privy/ tests/
	@printf "$(BOLD)Linting with ruff...$(RESET)\n"
	$(Q)uv run ruff check privy/ tests/ --fix
	$(call print_success,Formatting and linting complete)

.PHONY: dev_quality_check
dev_quality_check: ## Run all quality checks (format, lint, typecheck)
	$(call print_info_section,Running quality checks)
	@printf "$(BOLD)Checking format with black...$(RESET)\n"
	$(Q)uv run black --check privy/ tests/
	@printf "$(BOLD)Checking imports with isort...$(RESET)\n"
	$(Q)uv run isort --check privy/ tests/
	@printf "$(BOLD)Linting with ruff...$(RESET)\n"
	$(Q)uv run ruff check privy/ tests/
	@printf "$(BOLD)Type checking with mypy...$(RESET)\n"
	$(Q)uv run mypy privy/
	$(call print_success,All quality checks passed)

.PHONY: dev_todo
dev_todo: ## Find all TODO/FIXME/HACK comments in codebase
	$(call print_info_section,Searching for TODO comments)
	@grep -rn --color=always \
		--exclude-dir={venv,.venv,env,ENV,.uv,__pycache__,.pytest_cache,.mypy_cache,.tox,build,dist,*.egg-info,.git} \
		--exclude={"*.pyc","*.pyo","*.log","uv.lock"} \
		-E "(TODO|TODO_IMPROVE|TODO_IN_THIS_PR|FIXME|HACK|NOTE):" . || printf "$(GREEN)No TODOs found!$(RESET)\n"

.PHONY: clean_dev
clean_dev: ## Clean development artifacts
	$(call print_warning,Cleaning development artifacts)
	$(Q)find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	$(Q)find . -type f -name "*.pyc" -delete
	$(Q)find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	$(Q)find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	$(Q)find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	$(Q)find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	$(Q)rm -rf htmlcov/ .coverage
	$(call print_success,Development artifacts cleaned)
