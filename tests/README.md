# Privy Python SDK Tests

Unit tests for the Privy Python SDK, focusing on custom extensions in `lib/`.

## Setup

Install test dependencies:

```bash
pip install -e ".[dev]"
```

Or install individually:

```bash
pip install pytest pytest-asyncio pytest-httpx
```

## Running Tests

Run all tests:

```bash
pytest
```

Run with verbose output:

```bash
pytest -v
```

Run specific test file:

```bash
pytest tests/test_import_wallet.py
```

Run specific test:

```bash
pytest tests/test_import_wallet.py::TestImportWallet::test_import_wallet_complete_flow
```

## Test Coverage

Current test files:

- `test_import_wallet.py` - Tests for wallet import functionality
  - `import_wallet_init()` - Initialization and encryption key retrieval
  - `import_wallet_submit()` - Encrypted wallet submission
  - `import_wallet()` - Complete flow with HPKE encryption
  - Async variants of all functions

## What We Test

- **HPKE Integration**: Verify proper encryption using the `seal()` function
- **Function Flow**: Ensure `import_wallet()` correctly orchestrates init → encrypt → submit
- **Request Payloads**: Validate correct parameters are sent to API endpoints
- **Async Parity**: Ensure async and sync implementations behave identically

## What We Don't Test

- API endpoint implementation (Privy's responsibility)
- Auto-generated code in `resources/` (will be regenerated)
- Full integration tests (would require staging credentials)

## Adding New Tests

When adding custom extensions to `lib/`, follow this pattern:

1. Create test file: `tests/test_<feature>.py`
2. Mock HTTP calls using `httpx_mock` fixture
3. Test both sync and async variants
4. Focus on custom logic, not auto-generated code
