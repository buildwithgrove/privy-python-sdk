"""Example: Delete a Privy policy.

This script demonstrates how to use the delete() method to remove an existing
policy. This operation requires authorization signatures.

Environment variables required:
- PRIVY_APP_ID: Your Privy app ID
- PRIVY_APP_SECRET: Your Privy app secret
- PRIVY_AUTHORIZATION_KEY: Authorization key for signing requests
- PRIVY_POLICY_ID: ID of the policy to delete
"""

import os
from privy import PrivyAPI
from privy.lib.authorization_context import AuthorizationContext


def main():
    # Load environment variables
    app_id = os.environ["PRIVY_APP_ID"]
    app_secret = os.environ["PRIVY_APP_SECRET"]
    authorization_key = os.environ["PRIVY_AUTHORIZATION_KEY"]
    policy_id = os.environ["PRIVY_POLICY_ID"]

    # Initialize Privy client
    client = PrivyAPI(
        app_id=app_id,
        app_secret=app_secret,
    )

    # Create authorization context with the authorization key
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key(authorization_key)
        .build()
    )

    # Delete the policy
    print(f"Deleting policy {policy_id}...")

    client.policies.delete(
        policy_id=policy_id,
        authorization_context=auth_context,
    )

    print("Policy deleted successfully!")


if __name__ == "__main__":
    main()
