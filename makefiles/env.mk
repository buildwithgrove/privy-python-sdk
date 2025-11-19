##########################
### Environment Setup  ###
##########################

.PHONY: env_install
env_install: ## Install production dependencies
	$(call print_info_section,Installing production dependencies)
	$(call check_command,uv)
	$(Q)uv sync --no-dev
	$(call print_success,Production dependencies installed)

.PHONY: env_install_dev
env_install_dev: ## Install development dependencies
	$(call print_info_section,Installing development dependencies)
	$(call check_command,uv)
	$(Q)uv sync --extra dev
	$(call print_success,Development dependencies installed)

.PHONY: env_sync
env_sync: ## Sync dependencies with lock file
	$(call print_info_section,Syncing dependencies)
	$(call check_command,uv)
	$(Q)uv sync --extra dev
	$(call print_success,Dependencies synced)

.PHONY: clean_env
clean_env: ## Clean virtual environment
	$(call print_warning,Removing virtual environment)
	$(Q)rm -rf venv .venv
	$(call print_success,Virtual environment removed)
