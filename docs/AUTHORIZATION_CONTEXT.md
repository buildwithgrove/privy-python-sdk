# Authorization Context <!-- omit in toc -->

Server-side request signing for the Privy Python SDK.

## Table of Contents <!-- omit in toc -->

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Signing Methods](#signing-methods)
  - [1. Authorization Keys](#1-authorization-keys)
  - [2. User JWTs](#2-user-jwts)
  - [3. Custom Signing Function](#3-custom-signing-function)
  - [4. Pre-computed Signatures](#4-pre-computed-signatures)
- [Builder Pattern](#builder-pattern)
- [API Reference](#api-reference)
  - [AuthorizationContext](#authorizationcontext)
  - [AuthorizationContextBuilder](#authorizationcontextbuilder)
  - [CustomSignFunction](#customsignfunction)
  - [SignatureResult](#signatureresult)
- [Examples](#examples)
- [Testing](#testing)
- [Limitations](#limitations)

## Overview

The `AuthorizationContext` provides an abstraction for automatic request signing in the Privy Python SDK, similar to the Java SDK's authorization context.

**Key features:**
- **Multiple signing methods**: Authorization keys, user JWTs, custom functions, pre-computed signatures
- **Builder pattern**: Ergonomic API for constructing contexts
- **Type-safe**: Full type hints and protocols
- **Flexible**: Combine multiple signing methods in one context

## Quick Start

```python
from privy import PrivyAPI
from privy.lib import AuthorizationContext

# Initialize client
client = PrivyAPI(
    app_id="your_app_id",
    app_secret="your_app_secret",
)

# Create authorization context
auth_context = (
    AuthorizationContext.builder()
    .add_authorization_private_key("your_base64_key")
    .build()
)

# Generate signatures for a request
signatures = auth_context.generate_signatures(
    request_method="POST",
    request_url="https://api.privy.io/v1/wallets/wallet_id/transactions",
    request_body={"to": "0x...", "value": "1000000000000000000"},
    app_id=client.app_id,
)
```

## Signing Methods

### 1. Authorization Keys

Sign requests using authorization private keys directly.

**Use case:** Simple server-side signing with stored keys.

```python
context = (
    AuthorizationContext.builder()
    .add_authorization_private_key("base64_encoded_key")
    .build()
)
```

**Features:**
- Direct ECDSA P-256 signatures
- Automatic prefix stripping (`wallet-auth:`)
- Support for multiple keys

### 2. User JWTs

Sign requests using user JWT tokens. The SDK requests signing keys and computes P256 signatures.

**Use case:** User-authenticated operations.

**Status:** Not yet implemented (raises `NotImplementedError`)

```python
context = (
    AuthorizationContext.builder()
    .add_user_jwt("user_jwt_token")
    .build()
)
```

### 3. Custom Signing Function

Delegate signing to external services (KMS, HSM) or custom logic.

**Use case:** Enterprise security requirements, hardware security modules.

```python
def kms_signer(request_method, request_url, request_body, app_id):
    # Call AWS KMS, Google Cloud KMS, etc.
    signature = call_kms_service(...)
    return {
        "signature": signature,
        "signer_public_key": None,
    }

context = (
    AuthorizationContext.builder()
    .set_custom_sign_function(kms_signer)
    .build()
)
```

### 4. Pre-computed Signatures

Include signatures computed separately from the SDK.

**Use case:** Signatures from external systems or different application components.

```python
from privy.lib import get_authorization_signature

# Compute signature externally
signature = get_authorization_signature(
    url="https://api.privy.io/v1/wallets/wallet_id/transactions",
    body={"to": "0x...", "value": "1000000000000000000"},
    method="POST",
    app_id="your_app_id",
    private_key="base64_encoded_key",
)

# Add to context
context = (
    AuthorizationContext.builder()
    .add_signature(signature)
    .build()
)
```

## Builder Pattern

The `AuthorizationContextBuilder` provides a fluent API:

**Chained (recommended):**
```python
context = (
    AuthorizationContext.builder()
    .add_authorization_private_key("key1")
    .add_authorization_private_key("key2")
    .build()
)
```

**Step-by-step:**
```python
builder = AuthorizationContext.builder()
builder.add_authorization_private_key("key1")
builder.add_authorization_private_key("key2")
context = builder.build()
```

**Conditional:**
```python
builder = AuthorizationContext.builder()

if use_primary_key:
    builder.add_authorization_private_key("primary_key")

if use_backup_key:
    builder.add_authorization_private_key("backup_key")

context = builder.build()
```

## API Reference

### AuthorizationContext

Main class for authorization contexts.

**Methods:**
- `builder() -> AuthorizationContextBuilder` - Create a new builder
- `generate_signatures(request_method, request_url, request_body, app_id) -> List[str]` - Generate all signatures
- `has_signing_methods: bool` - Check if any signing methods are configured

**Example:**
```python
context = AuthorizationContext.builder().build()
signatures = context.generate_signatures("POST", "https://...", {}, "app_id")
```

### AuthorizationContextBuilder

Builder for constructing `AuthorizationContext` instances.

**Methods:**
- `add_authorization_private_key(private_key: str) -> Self` - Add authorization key
- `add_user_jwt(jwt: str) -> Self` - Add user JWT
- `set_custom_sign_function(sign_function: CustomSignFunction) -> Self` - Set custom signer
- `add_signature(signature: str, signer_public_key: Optional[str]) -> Self` - Add pre-computed signature
- `build() -> AuthorizationContext` - Build the context

### CustomSignFunction

Protocol for custom signing functions.

**Signature:**
```python
def custom_signer(
    request_method: str,
    request_url: str,
    request_body: Dict[str, Any],
    app_id: str,
) -> SignatureResult:
    ...
```

**Returns:** `SignatureResult` with `signature` and optional `signer_public_key`

### SignatureResult

TypedDict for signature results.

**Fields:**
- `signature: str` - Base64-encoded signature
- `signer_public_key: Optional[str]` - Public key used for signing

## Examples

See `examples/authorization_context_examples.py` for comprehensive examples:

**Basic usage:**
```bash
python examples/authorization_context_examples.py
```

**Test suite:**
```bash
pytest tests/test_authorization_context.py -v
```

## Testing

Run the test suite:

```bash
# All tests
pytest tests/test_authorization_context.py -v

# Specific test
pytest tests/test_authorization_context.py::TestAuthorizationContext::test_builder_with_authorization_keys -v

# With coverage
pytest tests/test_authorization_context.py --cov=privy.lib.authorization_context
```

## Limitations

**Current limitations:**

1. **User JWT signing not implemented** - Raises `NotImplementedError`
   - Requires API integration to exchange JWTs for signing keys
   - Planned for future release

2. **No SDK method integration** - Methods don't accept `authorization_context` parameter yet
   - Use `generate_signatures()` manually
   - SDK integration planned

3. **Single custom sign function** - Can only set one custom signer
   - Use multiple authorization keys or signatures for multi-signer scenarios

**Workarounds:**

```python
# Instead of passing to SDK methods (not yet supported):
# response = client.wallets.transactions.create(..., authorization_context=context)

# Use generate_signatures() manually:
signatures = context.generate_signatures(
    request_method="POST",
    request_url="https://api.privy.io/v1/wallets/wallet_id/transactions",
    request_body={...},
    app_id=client.app_id,
)

# Then include signatures in request headers manually
# (requires custom HTTP client modifications)
```

---

**Implementation reference:**
- Core implementation: `privy/lib/authorization_context.py`
- Tests: `tests/test_authorization_context.py`
- Examples: `examples/authorization_context_examples.py`
