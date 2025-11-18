# Privy Python SDK

Python SDK for the Privy API - extracted from the official `privy-client` package.

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

## Requirements

- Python >=3.8
- See `pyproject.toml` for complete dependency list

## Documentation

For API documentation, visit [Privy Docs](https://docs.privy.io)

## License

MIT
