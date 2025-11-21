"""Example: Using AuthorizationContext with Key Quorums

This example demonstrates how to use AuthorizationContext to automatically
generate multiple signatures for key quorum operations.
"""

from privy import PrivyAPI
from privy.lib import AuthorizationContext


def example_key_quorum_update():
    """Update a key quorum with automatic signature generation."""
    # Initialize client
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Create a key quorum with 3 keys requiring 2 signatures (2-of-3)
    key_quorum = client.key_quorums.create(
        public_keys=["pubkey1", "pubkey2", "pubkey3"],
        authorization_threshold=2,
        display_name="Treasury Quorum",
    )
    print(f"Created key quorum: {key_quorum.id}")

    # Build authorization context with 2 private keys (for 2-of-3 quorum)
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("your_private_key_1")
        .add_authorization_private_key("your_private_key_2")
        .build()
    )

    # Update the key quorum with automatic signature generation
    # The SDK will automatically generate 2 signatures and include them
    updated_quorum = client.key_quorums.update(
        key_quorum_id=key_quorum.id,
        public_keys=["new_pubkey1", "new_pubkey2", "new_pubkey3"],
        authorization_threshold=2,
        authorization_context=auth_context,  # Automatically generates 2 signatures
    )
    print(f"Updated key quorum: {updated_quorum.id}")


def example_key_quorum_delete():
    """Delete a key quorum with automatic signature generation."""
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Build authorization context
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("key_1")
        .add_authorization_private_key("key_2")
        .build()
    )

    # Delete with automatic signature generation
    deleted_quorum = client.key_quorums.delete(
        key_quorum_id="quorum_id",
        authorization_context=auth_context,
    )
    print(f"Deleted key quorum: {deleted_quorum.id}")


def example_custom_signing_kms():
    """Use KMS for key quorum signatures."""
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Define custom signing function for KMS
    def kms_sign_key1(request_method, request_url, request_body, app_id):
        # Call AWS KMS, Google Cloud KMS, etc. for key 1
        signature = call_kms_for_key1(request_method, request_url, request_body, app_id)
        return {"signature": signature, "signer_public_key": None}

    def kms_sign_key2(request_method, request_url, request_body, app_id):
        # Call KMS for key 2
        signature = call_kms_for_key2(request_method, request_url, request_body, app_id)
        return {"signature": signature, "signer_public_key": None}

    # Build context with multiple KMS calls
    # Note: We can only set one custom function, so combine the logic
    def combined_kms_signer(request_method, request_url, request_body, app_id):
        # For true multi-signature, use multiple authorization keys instead
        # This example shows the pattern for a single KMS-based signature
        sig1 = kms_sign_key1(request_method, request_url, request_body, app_id)
        return sig1

    auth_context = (
        AuthorizationContext.builder()
        .set_custom_sign_function(combined_kms_signer)
        .build()
    )

    # Update with KMS signatures
    updated_quorum = client.key_quorums.update(
        key_quorum_id="quorum_id",
        public_keys=["pubkey1", "pubkey2"],
        authorization_context=auth_context,
    )
    print(f"Updated with KMS signatures: {updated_quorum.id}")


def example_threshold_signatures():
    """Example of 3-of-5 threshold signatures."""
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Create a 3-of-5 key quorum
    key_quorum = client.key_quorums.create(
        public_keys=["pk1", "pk2", "pk3", "pk4", "pk5"],
        authorization_threshold=3,
        display_name="Board Approval Quorum",
    )

    # To update, provide at least 3 signatures
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("private_key_1")
        .add_authorization_private_key("private_key_2")
        .add_authorization_private_key("private_key_3")
        .build()
    )

    # Update with 3-of-5 signatures
    updated_quorum = client.key_quorums.update(
        key_quorum_id=key_quorum.id,
        public_keys=["new_pk1", "new_pk2", "new_pk3", "new_pk4", "new_pk5"],
        authorization_threshold=3,
        authorization_context=auth_context,
    )
    print(f"Updated 3-of-5 quorum: {updated_quorum.id}")


def example_mixed_signing_methods():
    """Combine different signing methods for quorum operations."""
    client = PrivyAPI(
        app_id="your_app_id",
        app_secret="your_app_secret",
    )

    # Mix authorization keys and pre-computed signatures
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("key_1")  # Direct signing
        .add_signature("precomputed_sig_2")  # Pre-computed from external system
        .build()
    )

    # Update with mixed signatures
    updated_quorum = client.key_quorums.update(
        key_quorum_id="quorum_id",
        public_keys=["pubkey1", "pubkey2"],
        authorization_threshold=2,
        authorization_context=auth_context,
    )
    print(f"Updated with mixed signatures: {updated_quorum.id}")


# Mock KMS functions for the example
def call_kms_for_key1(method, url, body, app_id):
    """Mock KMS call for key 1."""
    # In production, this would call AWS KMS, Google Cloud KMS, etc.
    return "kms_signature_1"


def call_kms_for_key2(method, url, body, app_id):
    """Mock KMS call for key 2."""
    return "kms_signature_2"


if __name__ == "__main__":
    print("Key Quorum + AuthorizationContext Examples")
    print("=" * 60)
    print("\nNOTE: These examples require real API credentials and keys.")
    print("Uncomment specific examples to run them.\n")

    # Uncomment to run examples:
    # example_key_quorum_update()
    # example_key_quorum_delete()
    # example_custom_signing_kms()
    # example_threshold_signatures()
    # example_mixed_signing_methods()

    print("See the source code for usage examples.")
