# AuthorizationContext Quick Reference

## Import

```python
from privy.lib import AuthorizationContext
```

## Basic Usage

```python
# Create context
context = (
    AuthorizationContext.builder()
    .add_authorization_private_key("your_key")
    .build()
)

# Generate signatures
signatures = context.generate_signatures(
    request_method="POST",
    request_url="https://api.privy.io/v1/wallets/...",
    request_body={...},
    app_id="your_app_id"
)
```

## Builder Methods

| Method | Description |
|--------|-------------|
| `add_authorization_private_key(key)` | Add authorization key for signing |
| `add_user_jwt(jwt)` | Add user JWT (not yet implemented) |
| `set_custom_sign_function(func)` | Set custom signing function |
| `add_signature(sig, pubkey)` | Add pre-computed signature |
| `build()` | Build the context |

## Signing Methods

### 1. Authorization Keys
```python
context = (
    AuthorizationContext.builder()
    .add_authorization_private_key("key1")
    .add_authorization_private_key("key2")
    .build()
)
```

### 2. Custom Function (KMS)
```python
def kms_signer(method, url, body, app_id):
    return {"signature": "...", "signer_public_key": None}

context = (
    AuthorizationContext.builder()
    .set_custom_sign_function(kms_signer)
    .build()
)
```

### 3. Pre-computed Signatures
```python
context = (
    AuthorizationContext.builder()
    .add_signature("signature_base64")
    .build()
)
```

### 4. Combined
```python
context = (
    AuthorizationContext.builder()
    .add_authorization_private_key("key1")
    .set_custom_sign_function(kms_signer)
    .add_signature("sig1")
    .build()
)
```

## Testing

```bash
# Run tests
pytest tests/test_authorization_context.py -v

# Run examples
python examples/authorization_context_examples.py
```

## Documentation

- **Full docs:** `docs/AUTHORIZATION_CONTEXT.md`
- **Examples:** `examples/authorization_context_examples.py`
- **Tests:** `tests/test_authorization_context.py`
- **Summary:** `AUTHORIZATION_CONTEXT_SUMMARY.md`
