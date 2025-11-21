# Authorization Signature Bug Fixes - Summary

## Issues Fixed

### 1. Request Body Consumption (Critical Bug) ✅

**Problem:** `PrivyHTTPClient._prepare_request()` was consuming the request body stream when reading it for signature generation, leaving an empty body for the actual HTTP request.

**Fix:** `privy/lib/http_client.py:57-59`
```python
body_bytes = request.read()
request.stream = httpx.ByteStream(body_bytes)  # Restore the stream
```

**Impact:** Fixes 401 "No valid authorization signatures" errors on all RPC operations.

---

### 2. Missing Privy Headers in Signature Payload ✅

**Problem:** According to [Privy docs](https://docs.privy.io/api-reference/authorization-signatures), the signature payload should include **all Privy-specific headers** (prefixed with `privy-`), not just `privy-app-id`.

This includes:
- `privy-app-id` (required)
- `privy-idempotency-key` (optional)
- Any other `privy-*` headers

**Fix:** `privy/lib/http_client.py:69-76`
```python
# Extract Privy-specific headers for signature payload
privy_headers = {"privy-app-id": self.app_id}
for header_name, header_value in request.headers.items():
    if header_name.lower().startswith("privy-"):
        if header_name.lower() != "privy-authorization-signature":
            privy_headers[header_name.lower()] = header_value
```

**Impact:** Ensures signature payload matches Privy's specification exactly.

---

## Signature Payload Construction

The signature payload now correctly follows Privy's specification:

```python
payload = {
    "version": 1,
    "method": "POST",  # or PUT, PATCH, DELETE
    "url": "https://api.privy.io/v1/wallets/wallet_id/rpc",
    "body": {...},  # Request JSON body
    "headers": {
        "privy-app-id": "your_app_id",
        "privy-idempotency-key": "...",  # If present
        # ... other privy-* headers
    }
}
```

The payload is then:
1. **Canonicalized** per RFC 8785 (sorted keys, compact JSON)
2. **Signed** with ECDSA P-256 using the authorization private key
3. **Base64-encoded** and included in the `privy-authorization-signature` header

---

## Testing

### Verification Script

Run `test_signature_payload.py` to verify:
```bash
.venv/bin/python test_signature_payload.py
```

**Output:**
```
✅ JSON canonicalization (RFC 8785)
✅ Privy headers inclusion
```

### Integration Testing

1. **Reinstall SDK in your app:**
   ```bash
   uv pip install -e /path/to/privy-python-sdk --force-reinstall
   ```

2. **Restart your application** to pick up the changes

3. **Test RPC operations** (eth_sendTransaction, etc.)

4. **Check debug logs** - The enhanced logging will show:
   - Authorization signature presence/length
   - Request body content
   - Full request details on 401 errors

---

## Debug Logging Added

Enhanced logging in `PrivyHTTPClient.send()` for 401 errors shows:

```
================================================================================
PRIVY AUTHORIZATION ERROR - Full Request Details:
================================================================================
Method: POST
URL: https://api.privy.io/v1/wallets/wallet_id/rpc
Headers:
  Authorization: [PRESENT] (length: 123)
  privy-authorization-signature: [PRESENT] (length: 88)
  privy-app-id: cmhz4po2u02dwjl0cva4d0wra
  privy-idempotency-key: unique-key-123
Body: {"method":"eth_sendTransaction","params":{...}}
Response Status: 401
Response Body: {"error": "..."}
================================================================================
```

This helps diagnose:
- Missing authorization signatures
- Malformed request bodies
- Incorrect header configuration

---

## Files Modified

1. `privy/lib/http_client.py`
   - Fixed request body consumption (line 57-59)
   - Added Privy headers extraction (line 69-76)
   - Added enhanced 401 error logging (line 104-120)

2. `privy/lib/authorization_signatures.py`
   - Updated function signature to accept headers dict (line 18-52)

3. `tests/test_http_client.py`
   - Updated test assertions for new signature (line 50)

4. `test_signature_payload.py` (new)
   - Verification script for payload construction

---

## Backward Compatibility

The `get_authorization_signature()` function maintains backward compatibility:

```python
# Old API (still works)
sig = get_authorization_signature(
    url="...",
    body={...},
    method="POST",
    app_id="your_app_id",
    private_key="key"
)

# New API (recommended)
sig = get_authorization_signature(
    url="...",
    body={...},
    method="POST",
    private_key="key",
    headers={"privy-app-id": "your_app_id", "privy-idempotency-key": "..."}
)
```

---

## Next Steps

1. **Test in your application** - The fixes are installed, restart and test
2. **Monitor debug logs** - Check for any remaining 401 errors
3. **Verify authorization key** - Ensure `PRIVY_AUTHORIZATION_KEY` is set correctly
4. **Check key expiration** - Authorization keys from Privy Dashboard can expire

---

## Related Documentation

- [Privy Authorization Signatures](https://docs.privy.io/api-reference/authorization-signatures)
- [RFC 8785 - JSON Canonicalization](https://www.rfc-editor.org/rfc/rfc8785)
- [ECDSA P-256](https://en.wikipedia.org/wiki/Elliptic_Curve_Digital_Signature_Algorithm)
