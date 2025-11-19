# Makefile Usage Guide

This document provides an overview of the Makefile targets available for the Privy Python SDK.

## Quick Start

```bash
# Complete developer setup (install + test)
make quickstart_dev

# Or step by step:
make install  # Install dependencies
make test     # Run tests
make format   # Format code
```

## Common Commands

### Development Workflow

```bash
# Install dependencies
make install                  # Install dev dependencies (alias for env_install_dev)

# Run tests
make test                     # Run all unit tests (alias for test_unit)
make test_unit_coverage       # Run tests with coverage report
make test_watch               # Run tests in watch mode

# Code quality
make format                   # Format and lint code (alias for dev_quality_format)
make check                    # Run all quality checks (alias for dev_quality_check)

# Build
make build                    # Build distribution packages (alias for build_package)
```

### Environment Management

```bash
make env_install              # Install production dependencies only
make env_install_dev          # Install development dependencies
make env_sync                 # Sync dependencies with lock file
make clean_env                # Remove virtual environment
```

### Testing

```bash
make test_unit                # Run unit tests
make test_unit_coverage       # Run tests with coverage
make test_watch               # Run tests in watch mode
make test_specific FILE=tests/test_import_wallet.py  # Run specific test file
```

### Code Quality

```bash
make dev_quality_format       # Format code (black, isort, ruff)
make dev_quality_check        # Check format + lint + typecheck
make dev_todo                 # Find all TODO/FIXME/HACK comments
```

### Building & Distribution

```bash
make build_package            # Build distribution packages
make build_check              # Check package build
make build_install_local      # Install in editable mode
make clean_build              # Clean build artifacts
```

### Cleaning

```bash
make clean                    # Clean all artifacts (dev + env + build)
make clean_dev                # Clean development artifacts only
make clean_env                # Clean virtual environment only
make clean_build              # Clean build artifacts only
```

## Makefile Structure

The Makefile is modular and organized into several files:

```
Makefile              # Main entry point with help system
makefiles/
├── colors.mk         # Color definitions and print helpers
├── common.mk         # Common utilities (command checks, etc.)
├── env.mk            # Environment/dependency management
├── test.mk           # Testing targets
├── dev.mk            # Development quality targets
└── build.mk          # Build and distribution targets
```

## Customization

### Adding New Targets

1. Add targets to the appropriate file in `makefiles/`
2. Use the naming convention: `<category>_<action>`
   - `env_*` - Environment/dependency management
   - `test_*` - Testing
   - `dev_*` - Development tools
   - `build_*` - Build and distribution
   - `clean_*` - Cleanup operations

3. Add a description comment with `##`
   ```makefile
   .PHONY: test_integration
   test_integration: ## Run integration tests
       $(call print_info_section,Running integration tests)
       $(Q)uv run pytest tests/integration/ -v
       $(call print_success,Integration tests passed)
   ```

### Using Print Helpers

Available helpers from `colors.mk`:

```makefile
$(call print_success,Message)    # Green checkmark
$(call print_error,Message)      # Red cross
$(call print_warning,Message)    # Yellow warning
$(call print_info,Message)       # Cyan info
$(call print_info_section,Title) # Bold cyan section header
```

### Quiet Mode

By default, commands are quiet (only output is shown). To see the actual commands being run:

```bash
make test Q=  # Show verbose output
```

## Examples

### Running Tests After Code Changes

```bash
# Format, check, and test
make format && make check && make test
```

### Building a Release

```bash
# Clean, format, test, and build
make clean && make format && make test && make build
```

### Development Loop

```bash
# Watch tests while developing
make test_watch
```

## Help

```bash
# Show all available targets
make help

# Unknown target? You'll get a helpful error
make unknown_target
# ❌ Error: Unknown target 'unknown_target'
# 💡 Available targets:
#    Run make help to see all available targets
```
