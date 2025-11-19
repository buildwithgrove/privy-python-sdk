"""Future SDK integration example for AuthorizationContext.

This file demonstrates the intended API once SDK methods are updated to
accept authorization_context parameters. This integration is not yet implemented.

See AUTHORIZATION_CONTEXT.md for current usage patterns.
"""

from privy import PrivyAPI
from privy.lib import AuthorizationContext


# TODO_IN_THIS_PR: Integrate authorization_context into SDK resource methods
# This requires updating the following files:
# - privy/resources/wallets/transactions.py
# - privy/resources/policies.py
# - privy/resources/key_quorums.py
# - Other resources that require signing


def future_example_transaction_signing():
    """Example of intended API for transaction signing with authorization context.

    Once implemented, this is how users will use AuthorizationContext.
    """
    # Initialize client
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Build authorization context
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("your_authorization_key")
        .build()
    )

    # Send transaction with automatic signing
    # NOTE: This API is not yet implemented
    # response = client.wallets.transactions.create(
    #     wallet_id="wallet_id",
    #     chain_type="ethereum",
    #     transaction={
    #         "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
    #         "value": "1000000000000000000",  # 1 ETH in wei
    #     },
    #     authorization_context=auth_context,  # <- This parameter doesn't exist yet
    # )
    #
    # print(f"Transaction hash: {response.transaction_hash}")


def future_example_policy_update():
    """Example of intended API for policy updates with authorization context."""
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Use custom signing function for KMS integration
    def kms_signer(request_method, request_url, request_body, app_id):
        # Call your KMS service
        signature = "signature_from_kms"
        return {"signature": signature, "signer_public_key": None}

    auth_context = (
        AuthorizationContext.builder()
        .set_custom_sign_function(kms_signer)
        .build()
    )

    # Update policy with automatic signing
    # NOTE: This API is not yet implemented
    # response = client.policies.update(
    #     policy_id="policy_id",
    #     threshold=2,
    #     authorization_context=auth_context,  # <- This parameter doesn't exist yet
    # )


def future_example_with_user_jwt():
    """Example of intended API for user JWT-based signing.

    Once user JWT signing is implemented, this will work.
    """
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Get user JWT from your auth flow
    user_jwt = "user_jwt_token_from_privy_auth"

    # Build context with user JWT
    auth_context = (
        AuthorizationContext.builder()
        .add_user_jwt(user_jwt)
        .build()
    )

    # NOTE: This will raise NotImplementedError until user JWT signing is implemented
    # response = client.wallets.transactions.create(
    #     wallet_id="wallet_id",
    #     chain_type="ethereum",
    #     transaction={...},
    #     authorization_context=auth_context,
    # )


def current_workaround_example():
    """Current workaround until SDK integration is complete.

    Use this pattern today to manually generate and include signatures.
    """
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Build authorization context
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("your_authorization_key")
        .build()
    )

    # Prepare request details
    request_url = "https://api.privy.io/v1/wallets/wallet_id/transactions"
    request_body = {
        "to": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "value": "1000000000000000000",
    }

    # Generate signatures manually
    signatures = auth_context.generate_signatures(
        request_method="POST",
        request_url=request_url,
        request_body=request_body,
        app_id=client.app_id,
    )

    print(f"Generated {len(signatures)} signature(s):")
    for i, sig in enumerate(signatures, 1):
        print(f"  {i}. {sig[:50]}...")

    # TODO: Include signatures in request headers
    # This requires either:
    # 1. Extending PrivyHTTPClient to accept per-request signatures
    # 2. Using httpx directly with custom headers
    # 3. Waiting for full SDK integration


# Implementation roadmap:
#
# Phase 1: ✅ Core AuthorizationContext (DONE)
#   - Builder pattern
#   - Authorization key signing
#   - Custom sign function support
#   - Pre-computed signatures
#   - Unit tests
#
# Phase 2: TODO - SDK Integration
#   - Add authorization_context parameter to resource methods:
#     * wallets.transactions.create()
#     * policies.update()
#     * key_quorums operations
#   - Update HTTP client to handle per-request signatures
#   - Integration tests
#
# Phase 3: TODO - User JWT Signing
#   - Implement JWT → signing key exchange
#   - Add signature generation with user keys
#   - End-to-end tests
#
# Phase 4: TODO - Advanced Features
#   - Key quorum signing
#   - Multiple user JWT support
#   - Async custom sign functions
#   - Signature caching/reuse


if __name__ == "__main__":
    print("Authorization Context Integration Examples")
    print("=" * 60)
    print("\nNOTE: These examples show the intended future API.")
    print("See examples/authorization_context_examples.py for current usage.\n")

    print("Current workaround:")
    print("-" * 60)
    current_workaround_example()
