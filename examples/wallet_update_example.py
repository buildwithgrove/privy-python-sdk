#!/usr/bin/env python3
"""Example: Update wallet with AuthorizationContext

This example demonstrates how to update a wallet's policy using
the AuthorizationContext for automatic signature generation.
"""

from privy import PrivyAPI
from privy.lib.authorization_context import AuthorizationContext

# Initialize the Privy client
client = PrivyAPI(
    app_id="your_app_id",
    app_secret="your_app_secret",
)

# Example 1: Update wallet policy with AuthorizationContext
# =========================================================
# Create an authorization context with the required signing keys
auth_context = (
    AuthorizationContext.builder()
    .add_authorization_private_key("base64_encoded_key_1")
    .add_authorization_private_key("base64_encoded_key_2")  # For 2-of-N quorum
    .build()
)

# Update the wallet with automatic signature generation
wallet = client.wallets.update(
    wallet_id="wallet_abc123",
    policy_ids=["policy_xyz789"],
    authorization_context=auth_context,  # Signatures generated automatically
)

print(f"✅ Wallet updated: {wallet.id}")
print(f"   New policies: {wallet.policy_ids}")


# Example 2: Update wallet owner
# ================================
wallet = client.wallets.update(
    wallet_id="wallet_abc123",
    owner_id="new_owner_key_quorum_id",
    authorization_context=auth_context,
)

print(f"✅ Wallet owner updated: {wallet.id}")


# Example 3: Manual signature (alternative approach)
# ===================================================
# You can still use manual signatures if needed
wallet = client.wallets.update(
    wallet_id="wallet_abc123",
    policy_ids=["policy_xyz789"],
    privy_authorization_signature="sig1,sig2",  # Comma-separated signatures
)


# Example 4: Async version
# =========================
import asyncio
from privy import AsyncPrivyAPI


async def update_wallet_async():
    client = AsyncPrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("base64_encoded_key_1")
        .build()
    )

    wallet = await client.wallets.update(
        wallet_id="wallet_abc123",
        policy_ids=["policy_xyz789"],
        authorization_context=auth_context,
    )

    print(f"✅ Async wallet updated: {wallet.id}")


# Run async example
# asyncio.run(update_wallet_async())


# Example 5: Update with custom sign function
# ============================================
def my_kms_signer(request_method: str, request_url: str, request_body: dict) -> str:
    """Custom signing function that uses a KMS or HSM."""
    # Call your KMS/HSM to generate signature
    # Return base64-encoded signature
    return "signature_from_kms"


auth_context = (
    AuthorizationContext.builder()
    .set_custom_sign_function(my_kms_signer)
    .build()
)

wallet = client.wallets.update(
    wallet_id="wallet_abc123",
    policy_ids=["policy_xyz789"],
    authorization_context=auth_context,
)

print("✅ Wallet updated with KMS signature")
