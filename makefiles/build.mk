####################
### Build & Dist  ###
####################

.PHONY: build_package
build_package: clean_build ## Build distribution packages
	$(call print_info_section,Building distribution packages)
	$(Q)uv build
	$(call print_success,Package built successfully)

.PHONY: build_install_local
build_install_local: build_package ## Install package locally in editable mode
	$(call print_info_section,Installing package in editable mode)
	$(Q)uv pip install -e .
	$(call print_success,Package installed in editable mode)

.PHONY: build_check
build_check: ## Check package build
	$(call print_info_section,Checking package build)
	$(Q)uv build --check
	$(call print_success,Package build check passed)

.PHONY: clean_build
clean_build: ## Clean build artifacts
	$(call print_warning,Cleaning build artifacts)
	$(Q)rm -rf build/ dist/ *.egg-info/
	$(call print_success,Build artifacts cleaned)
