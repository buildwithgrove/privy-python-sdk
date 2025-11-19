#####################
### Common Helpers ##
#####################

# Quiet mode by default (set Q= for verbose output)
Q := @

# Check if a command exists
define check_command
	@command -v $(1) >/dev/null 2>&1 || { \
		$(call print_error,$(1) is not installed); \
		exit 1; \
	}
endef
