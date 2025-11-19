"""Examples demonstrating AuthorizationContext usage for server-side signing.

The AuthorizationContext provides an abstraction for automatic request signing
using various methods: authorization keys, user JWTs, custom signing functions,
and pre-computed signatures.
"""

from privy import PrivyAPI
from privy.lib import AuthorizationContext


# Example 1: Signing with authorization keys
def example_authorization_keys():
    """Sign requests using authorization private keys.

    This is the simplest approach - use private keys directly to sign requests.
    """
    # Initialize client
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Build authorization context with one or more private keys
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("base64_encoded_key_1")
        .add_authorization_private_key("base64_encoded_key_2")  # Optional: add multiple keys
        .build()
    )

    # Use the context - signatures will be generated automatically
    # NOTE: SDK methods need to be updated to accept authorization_context parameter
    # This example shows the intended API once integration is complete
    # response = client.wallets.transactions.create(
    #     wallet_id="wallet_id",
    #     chain_type="ethereum",
    #     transaction={"to": "0x...", "value": "1000000000000000000"},
    #     authorization_context=auth_context
    # )

    # For now, you can generate signatures manually:
    # Note: This would fail with placeholder keys, so we just demonstrate the API
    print(f"Context configured with {len(auth_context._authorization_private_keys)} key(s)")
    print("Signatures would be generated when using real keys")


# Example 2: Signing with user JWTs
def example_user_jwts():
    """Sign requests using user JWT tokens.

    The SDK will request user signing keys and compute P256 signatures.
    Note: This feature is not yet implemented.
    """
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Build authorization context with user JWT
    auth_context = (
        AuthorizationContext.builder()
        .add_user_jwt("user_jwt_token")
        .build()
    )

    # This will raise NotImplementedError until user JWT signing is implemented
    print(f"Context configured with {len(auth_context._user_jwts)} JWT(s)")
    print("Note: User JWT signing raises NotImplementedError (not yet implemented)")


# Example 3: Signing with custom function (e.g., KMS)
def example_custom_signing_function():
    """Sign requests using a custom signing function.

    Use this when signing logic needs to occur in a separate service
    (e.g., AWS KMS, Google Cloud KMS, Azure Key Vault, HSM).
    """
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Define custom signing function
    def kms_sign_function(request_method, request_url, request_body, app_id):
        """Custom signing function that calls AWS KMS.

        In production, this would:
        1. Serialize the request data
        2. Call KMS to sign the data
        3. Return the signature
        """
        # Example: Call your KMS service
        # import boto3
        # kms = boto3.client('kms')
        # response = kms.sign(
        #     KeyId='your-key-id',
        #     Message=serialize_request(request_method, request_url, request_body, app_id),
        #     SigningAlgorithm='ECDSA_SHA_256'
        # )
        # signature = base64.b64encode(response['Signature']).decode('utf-8')

        # For demo purposes, return a mock signature
        return {
            "signature": "mock_signature_from_kms",
            "signer_public_key": None,
        }

    # Build authorization context with custom signing function
    auth_context = (
        AuthorizationContext.builder()
        .set_custom_sign_function(kms_sign_function)
        .build()
    )

    # Use the context
    signatures = auth_context.generate_signatures(
        request_method="POST",
        request_url="https://api.privy.io/v1/wallets/wallet_id/transactions",
        request_body={"to": "0x...", "value": "1000000000000000000"},
        app_id="your_app_id",
    )
    print(f"Generated signature via custom function: {signatures[0]}")


# Example 4: Using pre-computed signatures
def example_precomputed_signatures():
    """Use signatures computed separately from the SDK.

    This is useful if you compute signatures in a different part of your
    application or want to pass signatures from an external system.
    """
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Compute signature externally (using the authorization_signatures module)
    # In real usage, you would compute this with a real key
    signature = "mock_precomputed_signature_base64"

    # Add pre-computed signature to authorization context
    auth_context = (
        AuthorizationContext.builder()
        .add_signature(signature, signer_public_key=None)
        .build()
    )

    # Use the context
    signatures = auth_context.generate_signatures(
        request_method="POST",
        request_url="https://api.privy.io/v1/wallets/wallet_id/transactions",
        request_body={"to": "0x...", "value": "1000000000000000000"},
        app_id="your_app_id",
    )
    print(f"Using pre-computed signature: {signatures[0]}")


# Example 5: Combining multiple signing methods
def example_combined_methods():
    """Combine multiple signing methods in one context.

    You can mix authorization keys, custom functions, and pre-computed signatures.
    """
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    def custom_signer(request_method, request_url, request_body, app_id):
        return {"signature": "custom_signature", "signer_public_key": None}

    # Build context with multiple signing methods
    auth_context = (
        AuthorizationContext.builder()
        .set_custom_sign_function(custom_signer)
        .add_signature("precomputed_sig_1")
        .build()
    )

    # This will generate 2 signatures total:
    # 1. From custom_signer
    # 2. From precomputed_sig_1
    signatures = auth_context.generate_signatures(
        request_method="POST",
        request_url="https://api.privy.io/v1/wallets/wallet_id/transactions",
        request_body={},
        app_id="your_app_id",
    )
    print(f"Generated {len(signatures)} signatures from multiple methods")


# Example 6: Builder pattern variations
def example_builder_patterns():
    """Different ways to use the builder pattern."""

    # Method 1: Chained builder (most common)
    context1 = (
        AuthorizationContext.builder()
        .add_authorization_private_key("key1")
        .add_authorization_private_key("key2")
        .build()
    )

    # Method 2: Step-by-step builder
    builder = AuthorizationContext.builder()
    builder.add_authorization_private_key("key1")
    builder.add_authorization_private_key("key2")
    context2 = builder.build()

    # Method 3: Conditional building
    builder = AuthorizationContext.builder()

    # Add keys based on conditions
    use_primary_key = True
    use_backup_key = False

    if use_primary_key:
        builder.add_authorization_private_key("primary_key")

    if use_backup_key:
        builder.add_authorization_private_key("backup_key")

    context3 = builder.build()

    # Method 4: Direct instantiation (less ergonomic, not recommended)
    context4 = AuthorizationContext(
        authorization_private_keys=["key1", "key2"],
    )

    print("All builder patterns work!")


if __name__ == "__main__":
    print("AuthorizationContext Examples")
    print("=" * 50)

    print("\n1. Authorization Keys:")
    example_authorization_keys()

    print("\n2. User JWTs (not yet implemented):")
    example_user_jwts()

    print("\n3. Custom Signing Function:")
    example_custom_signing_function()

    print("\n4. Pre-computed Signatures:")
    example_precomputed_signatures()

    print("\n5. Combined Methods:")
    example_combined_methods()

    print("\n6. Builder Pattern Variations:")
    example_builder_patterns()
