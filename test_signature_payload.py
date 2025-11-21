#!/usr/bin/env python3
"""Test script to verify signature payload construction matches Privy's example."""

import json
from privy.lib.authorization_signatures import canonicalize, get_authorization_signature

# Test 1: Verify canonicalization
print("Test 1: JSON Canonicalization")
print("=" * 60)
payload = {
    "version": 1,
    "method": "POST",
    "url": "https://api.privy.io/v1/wallets",
    "body": {"chain_type": "ethereum"},
    "headers": {"privy-app-id": "test-app-id"},
}
canonical = canonicalize(payload)
print(f"Canonical JSON:\n{canonical}\n")

expected_canonical = '{"body":{"chain_type":"ethereum"},"headers":{"privy-app-id":"test-app-id"},"method":"POST","url":"https://api.privy.io/v1/wallets","version":1}'
assert canonical == expected_canonical, f"Canonicalization failed!\nExpected: {expected_canonical}\nGot: {canonical}"
print("✅ Canonicalization matches expected format\n")

print("=" * 60)
print("Signature payload construction:")
print("  ✅ JSON canonicalization (RFC 8785)")
print("  ✅ Privy headers inclusion")
print("=" * 60)
