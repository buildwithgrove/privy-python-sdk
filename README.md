# Privy Python SDK

Python SDK for the Privy API - extracted from the official `privy-client` package and properly packaged to avoid namespace conflicts.

## Installation

Install directly from GitHub using pip or uv:

```bash
# Using uv
uv add git+https://github.com/buildwithgrove/privy-python-sdk.git@main

# Using pip
pip install git+https://github.com/buildwithgrove/privy-python-sdk.git@main
```

## Usage

This is a drop-in replacement for `privy-client>=0.2.0`:

```python
from privy import PrivyAPI

# Initialize the client
client = PrivyAPI(
    app_id="your-app-id",
    app_secret="your-app-secret"
)

# Use the API
user = client.users.get(user_id="did:privy:...")
```

## Key Features

- **Proper namespace packaging**: No conflicts with Python's built-in `types` module
- **Drop-in replacement**: Same import structure as official package
- **Type-safe**: Includes `py.typed` marker for type checking support
- **Complete API coverage**: All resources, types, and utilities included

## Requirements

- Python >=3.8
- Dependencies: anyio, cryptography, distro, httpx, pydantic, pyhpke, pyjwt, sniffio, typing-extensions, web3

## Package Structure

```
privy/
├── __init__.py          # Main package exports
├── _client.py           # Client implementation
├── lib/                 # Internal library utilities
│   ├── users.py         # User encryption/decryption utilities
│   ├── wallets.py       # Wallet provider utilities
│   └── http_client.py   # Custom HTTP client
├── types/               # Type definitions (properly namespaced as privy.types)
├── resources/           # API resources
└── _utils/              # Utility functions
```

## Documentation

For API documentation, visit [Privy Docs](https://docs.privy.io)

## License

MIT
