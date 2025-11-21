# Wallet Update with AuthorizationContext - Implementation Summary

## Overview

Implemented `wallets.update()` method with `AuthorizationContext` support, following the same pattern as `key_quorums.update()`.

## What Was Added

### 1. Extended `WalletsResource` class

**File:** `privy/lib/wallets.py`

- Added `update()` method with `authorization_context` parameter
- Both sync and async variants implemented
- Follows the same pattern as `key_quorums.update()`

### 2. Shared Helper Function

**Function:** `_prepare_authorization_headers()`

Handles the common pattern of:
1. Generating signatures from `AuthorizationContext`, OR
2. Using manually provided `privy_authorization_signature`

This helper is reusable across all resources (wallets, policies, transactions, etc.)

### 3. Documentation & Examples

- **Example file:** `examples/wallet_update_example.py`
- Shows 5 usage patterns:
  1. Update wallet policy with AuthorizationContext
  2. Update wallet owner
  3. Manual signature (backwards compatible)
  4. Async version
  5. Custom sign function (KMS integration)

## API

### Sync Version

```python
def update(
    self,
    wallet_id: str,
    *,
    additional_signers: Iterable[AdditionalSigner] | NotGiven = NOT_GIVEN,
    owner: Optional[Owner] | NotGiven = NOT_GIVEN,
    owner_id: Optional[str] | NotGiven = NOT_GIVEN,
    policy_ids: List[str] | NotGiven = NOT_GIVEN,
    authorization_context: Optional[AuthorizationContext] = None,
    privy_authorization_signature: str | NotGiven = NOT_GIVEN,
    extra_headers: Headers | None = None,
    extra_query: Query | None = None,
    extra_body: Body | None = None,
    timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
) -> Wallet
```

### Async Version

Same signature with `async def` and `-> Wallet` return type.

## Usage Examples

### Using AuthorizationContext (Recommended)

```python
from privy import PrivyAPI
from privy.lib.authorization_context import AuthorizationContext

client = PrivyAPI(app_id="...", app_secret="...")

# Create authorization context with signing keys
auth_context = (
    AuthorizationContext.builder()
    .add_authorization_private_key("key1")
    .add_authorization_private_key("key2")
    .build()
)

# Update wallet - signatures generated automatically
wallet = client.wallets.update(
    wallet_id="wallet_abc123",
    policy_ids=["policy_xyz789"],
    authorization_context=auth_context,
)
```

### Using Manual Signatures (Backwards Compatible)

```python
# Still works for manual signature passing
wallet = client.wallets.update(
    wallet_id="wallet_abc123",
    policy_ids=["policy_xyz789"],
    privy_authorization_signature="sig1,sig2",
)
```

### Async Usage

```python
from privy import AsyncPrivyAPI

client = AsyncPrivyAPI(app_id="...", app_secret="...")

wallet = await client.wallets.update(
    wallet_id="wallet_abc123",
    policy_ids=["policy_xyz789"],
    authorization_context=auth_context,
)
```

## Implementation Pattern

This implementation follows the established pattern from `key_quorums.update()`:

1. **Extend the base resource class** in `privy/lib/`
2. **Override the method** to add `authorization_context` parameter
3. **Use `_prepare_authorization_headers()`** to generate signatures
4. **Call parent's `_patch()`** with generated headers
5. **Implement both sync and async versions**

## Files Modified

1. **`privy/lib/wallets.py`**
   - Added `_prepare_authorization_headers()` helper (lines 21-54)
   - Extended `WalletsResource.update()` (lines 97-202)
   - Extended `AsyncWalletsResource.update()` (lines 457-534)
   - Added imports for AuthorizationContext and utils

2. **`examples/wallet_update_example.py`** (new)
   - Comprehensive usage examples

3. **`WALLET_UPDATE_IMPLEMENTATION.md`** (new, this file)
   - Implementation documentation

## Benefits

1. **Ergonomic API** - Automatic signature generation
2. **Backwards compatible** - Still supports manual signatures
3. **Multi-key support** - Easy 2-of-N quorum signing
4. **KMS integration** - Custom sign function support
5. **Consistent pattern** - Same as `key_quorums.update()`
6. **Type safe** - Full type hints and IDE autocomplete

## Testing

### Manual Testing

```python
# Test that the method exists with correct parameters
from privy import PrivyAPI
import inspect

client = PrivyAPI(app_id='test', app_secret='test')
sig = inspect.signature(client.wallets.update)

assert 'authorization_context' in sig.parameters
assert 'privy_authorization_signature' in sig.parameters
print("✅ All parameters present")
```

### Integration Testing

See `examples/wallet_update_example.py` for integration test patterns.

## Next Steps

### Recommended: Apply Same Pattern to Other Resources

1. **`privy/lib/transactions.py`**
   - Currently a TODO stub
   - Implement `create()` with `authorization_context`

2. **`privy/lib/policies.py`**
   - Currently a TODO stub
   - Implement `update()` and `delete()` with `authorization_context`

3. **Shared Helper Module** (Optional)
   - Consider moving `_prepare_authorization_headers()` to `privy/lib/_resource_helpers.py`
   - Avoids duplication across `wallets.py`, `key_quorums.py`, `transactions.py`, `policies.py`

## Consistency Check

Comparing with `key_quorums.update()`:

| Feature                    | key_quorums.update() | wallets.update() | Status |
| -------------------------- | -------------------- | ---------------- | ------ |
| authorization_context param| ✅                   | ✅               | ✅     |
| Manual signature support   | ✅                   | ✅               | ✅     |
| Helper function            | ✅                   | ✅               | ✅     |
| Sync version               | ✅                   | ✅               | ✅     |
| Async version              | ✅                   | ✅               | ✅     |
| Docstring with examples    | ✅                   | ✅               | ✅     |

**Result:** Full consistency achieved! ✅

## SDK Integration Complete

The `wallets.update()` method is now fully integrated with `AuthorizationContext` and ready to use!
