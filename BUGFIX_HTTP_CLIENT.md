# HTTP Client Request Body Consumption Bug Fix

## Problem

When using `client.update_authorization_key()` to configure authorization signing, RPC requests (like `eth_sendTransaction`) were failing with 401 errors:

```
Error code: 401 - {'error': 'No valid authorization signatures were provided...'}
```

## Root Cause

In `privy/lib/http_client.py:48`, the `_prepare_request()` method was consuming the request body stream when reading it to generate the authorization signature:

```python
body_str = request.read().decode("utf-8")  # Consumes the stream!
```

After calling `request.read()`, the stream was exhausted. When httpx tried to send the actual request, the body was **empty**, causing the API to reject it.

## Fix

**File:** `privy/lib/http_client.py:50-52`

```python
# Read the body content and then restore the stream
body_bytes = request.read()
# Restore the stream so httpx can read it again when sending
request.stream = httpx.ByteStream(body_bytes)
```

This ensures the request body is available both for:
1. Signature generation (our code)
2. Actual request transmission (httpx)

## Verification

Added comprehensive test coverage in `tests/test_http_client.py`:

- ✅ `test_request_body_not_consumed` - Verifies body is readable after signature generation
- ✅ `test_no_signature_without_authorization_key` - No signing when key not set
- ✅ `test_no_signature_for_get_requests` - GET requests not signed
- ✅ `test_authorization_key_can_be_updated` - Key updates work
- ✅ `test_empty_body_handled_gracefully` - Empty bodies don't cause errors

All tests pass:
```bash
pytest tests/test_http_client.py -v
# 5 passed in 0.40s
```

## Impact

This fix resolves the 401 errors for any operation using the authorization key:
- `wallets.rpc()` - All RPC methods (eth_sendTransaction, etc.)
- Future resources that use authorization signatures

## Related Code

The authorization key flow:
1. User calls `client.update_authorization_key(key)` - Sets key on HTTP client
2. User makes RPC request via `client.wallets.rpc(...)`
3. `PrivyHTTPClient._prepare_request()` generates signature from request body
4. Signature is added to `privy-authorization-signature` header
5. Request is sent with both body and signature

Before this fix, step 3 consumed the body, causing step 5 to send an empty request.
