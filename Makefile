##############################
### Privy Python SDK       ###
### Makefile               ###
##############################

.DEFAULT_GOAL := help

.PHONY: help
help: ## Show all available targets with descriptions
	@printf "\n"
	@printf "$(BOLD)$(CYAN)🔐 Privy Python SDK - Makefile Targets$(RESET)\n"
	@printf "\n"
	@printf "$(BOLD)=== 🚀 Quick Start ===$(RESET)\n"
	@grep -h -E '^quickstart.*:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-40s$(RESET) %s\n", $$1, $$2}'
	@printf "\n"
	@printf "$(BOLD)=== 🐍 Environment Setup ===$(RESET)\n"
	@grep -h -E '^env_.*:.*?## .*$$' $(MAKEFILE_LIST) ./makefiles/*.mk 2>/dev/null | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-40s$(RESET) %s\n", $$1, $$2}' | sort -u
	@printf "\n"
	@printf "$(BOLD)=== 🧪 Testing ===$(RESET)\n"
	@grep -h -E '^test_.*:.*?## .*$$' $(MAKEFILE_LIST) ./makefiles/*.mk 2>/dev/null | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-40s$(RESET) %s\n", $$1, $$2}' | sort -u
	@printf "\n"
	@printf "$(BOLD)=== 🛠️  Development ===$(RESET)\n"
	@grep -h -E '^dev_.*:.*?## .*$$' $(MAKEFILE_LIST) ./makefiles/*.mk 2>/dev/null | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-40s$(RESET) %s\n", $$1, $$2}' | sort -u
	@printf "\n"
	@printf "$(BOLD)=== 📦 Build & Distribution ===$(RESET)\n"
	@grep -h -E '^build_.*:.*?## .*$$' $(MAKEFILE_LIST) ./makefiles/*.mk 2>/dev/null | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-40s$(RESET) %s\n", $$1, $$2}' | sort -u
	@printf "\n"
	@printf "$(BOLD)=== 🧹 Cleaning ===$(RESET)\n"
	@grep -h -E '^clean.*:.*?## .*$$' $(MAKEFILE_LIST) ./makefiles/*.mk 2>/dev/null | awk 'BEGIN {FS = ":.*?## "}; {printf "$(CYAN)%-40s$(RESET) %s\n", $$1, $$2}' | sort -u
	@printf "\n"

##################
### Quick Start ##
##################

.PHONY: quickstart_dev
quickstart_dev: ## Complete developer setup (install deps + run tests)
	@printf "\n"
	@printf "$(BOLD)$(GREEN)🔐 Privy Python SDK - Developer Quick Start$(RESET)\n"
	@printf "\n"
	@printf "$(BOLD)Step 1:$(RESET) Install development dependencies\n"
	@printf "   $(CYAN)make env_install_dev$(RESET)\n"
	@printf "\n"
	@$(MAKE) env_install_dev
	@printf "\n"
	@printf "$(GREEN)✓ Dependencies installed$(RESET)\n"
	@printf "\n"
	@printf "$(BOLD)Step 2:$(RESET) Run tests\n"
	@printf "   $(CYAN)make test_unit$(RESET)\n"
	@printf "\n"
	@$(MAKE) test_unit
	@printf "\n"
	@printf "$(GREEN)✓ All tests passed$(RESET)\n"
	@printf "\n"
	@printf "$(BOLD)Step 3:$(RESET) Run quality checks\n"
	@printf "   $(CYAN)make dev_quality_check$(RESET)\n"
	@printf "\n"
	@printf "$(BOLD)$(GREEN)✓ Developer setup complete! Happy coding! 🔐$(RESET)\n"
	@printf "\n"
	@printf "$(BOLD)Next steps:$(RESET)\n"
	@printf "  • Format code:       $(CYAN)make dev_quality_format$(RESET)\n"
	@printf "  • Run tests:         $(CYAN)make test_unit$(RESET)\n"
	@printf "  • Build package:     $(CYAN)make build_package$(RESET)\n"
	@printf "  • View all commands: $(CYAN)make help$(RESET)\n"
	@printf "\n"

################
### Imports  ###
################

include ./makefiles/colors.mk
include ./makefiles/common.mk
include ./makefiles/env.mk
include ./makefiles/test.mk
include ./makefiles/dev.mk
include ./makefiles/build.mk

############################
### Target Aliases       ###
############################

.PHONY: install
install: env_install_dev ## Alias for env_install_dev

.PHONY: test
test: test_unit ## Alias for test_unit

.PHONY: format
format: dev_quality_format ## Alias for dev_quality_format

.PHONY: check
check: dev_quality_check ## Alias for dev_quality_check

.PHONY: build
build: build_package ## Alias for build_package

.PHONY: clean
clean: clean_dev clean_env clean_build ## Clean up all generated files
	$(call print_success,All cleanup complete)

###############################
###  Global Error Handling  ###
###############################

# Catch-all for undefined targets
%:
	@TARGET="$@"; \
	printf "\n"; \
	printf "$(RED)❌ Error: Unknown target '$(BOLD)%s$(RESET)$(RED)'$(RESET)\n" "$$TARGET"; \
	printf "\n"; \
	printf "$(YELLOW)💡 Available targets:$(RESET)\n"; \
	printf "   Run $(CYAN)make help$(RESET) to see all available targets\n"; \
	printf "\n"; \
	exit 1
