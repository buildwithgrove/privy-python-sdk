"""Example: Add a rule to an existing Privy policy.

This script demonstrates how to use the add_rule() method to add a new rule
to an existing policy without replacing existing rules.

Environment variables required:
- PRIVY_APP_ID: Your Privy app ID
- PRIVY_APP_SECRET: Your Privy app secret
- PRIVY_AUTHORIZATION_KEY: Authorization key for signing requests
- PRIVY_POLICY_ID: ID of the policy to add the rule to
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

    # Add rule to the policy
    print(f"Adding rule to policy {policy_id}...")

    result = client.policies.add_rule(
        policy_id=policy_id,
        name="Allow all ETH Send Transactions",
        method="eth_sendTransaction",
        action="ALLOW",
        conditions=[
            {
                "field_source": "system",
                "field": "current_unix_timestamp",
                "operator": "gt",
                "value": "1"
            }
        ],
        authorization_context=auth_context,
    )

    print("Rule added successfully!")
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
