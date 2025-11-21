"""Example: Delete a rule from a Privy policy.

This script demonstrates how to remove a specific rule from an existing policy.
Since the Privy API doesn't have a dedicated rule deletion endpoint, we:
1. Fetch the current policy to get all rules
2. Filter out the rule we want to delete (by name or index)
3. Update the policy with the filtered rules list

Environment variables required:
- PRIVY_APP_ID: Your Privy app ID
- PRIVY_APP_SECRET: Your Privy app secret
- PRIVY_AUTHORIZATION_KEY: Authorization key for signing requests
- PRIVY_POLICY_ID: ID of the policy containing the rule
- PRIVY_RULE_ID: ID of the rule to delete (optional, highest priority)
- PRIVY_RULE_NAME: Name of the rule to delete (optional, will delete by index if not provided)
- PRIVY_RULE_INDEX: Index of the rule to delete (optional, defaults to 0 if rule name/ID not provided)
"""

import os
import json
from privy import PrivyAPI
from privy.lib.authorization_context import AuthorizationContext


def serialize_pydantic(obj):
    """Recursively convert Pydantic objects to dicts."""
    if hasattr(obj, "__dict__"):
        # It's a Pydantic model - manually extract attributes
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith("_"):
                result[key] = serialize_pydantic(value)
        return result
    elif isinstance(obj, list):
        return [serialize_pydantic(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize_pydantic(value) for key, value in obj.items()}
    else:
        return obj


def main():
    # Load environment variables
    app_id = os.environ["PRIVY_APP_ID"]
    app_secret = os.environ["PRIVY_APP_SECRET"]
    authorization_key = os.environ["PRIVY_AUTHORIZATION_KEY"]
    policy_id = os.environ["PRIVY_POLICY_ID"]
    rule_id = os.environ.get("PRIVY_RULE_ID")
    rule_name = os.environ.get("PRIVY_RULE_NAME")
    rule_index = int(os.environ.get("PRIVY_RULE_INDEX", "0"))

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

    # Step 1: Fetch the current policy
    print(f"Fetching policy {policy_id}...")
    policy = client.policies.get(policy_id=policy_id)

    current_rules = policy.rules
    print(f"Policy currently has {len(current_rules)} rule(s)")

    if not current_rules:
        print("No rules to delete!")
        return

    # Step 2: Filter out the rule to delete
    if rule_id:
        # Delete by rule ID (highest priority)
        print(f"Looking for rule with ID: {rule_id}")
        filtered_rules = [rule for rule in current_rules if getattr(rule, "id", None) != rule_id]

        if len(filtered_rules) == len(current_rules):
            print(f"Rule with ID '{rule_id}' not found!")
            return

        deleted_rule_identifier = f"ID {rule_id}"
    elif rule_name:
        # Delete by rule name
        print(f"Looking for rule with name: {rule_name}")
        filtered_rules = [rule for rule in current_rules if getattr(rule, "name", None) != rule_name]

        if len(filtered_rules) == len(current_rules):
            print(f"Rule with name '{rule_name}' not found!")
            return

        deleted_rule_identifier = f"name '{rule_name}'"
    else:
        # Delete by index
        if rule_index >= len(current_rules):
            print(f"Rule index {rule_index} out of range (policy has {len(current_rules)} rules)")
            return

        deleted_rule = current_rules[rule_index]
        deleted_rule_identifier = f"at index {rule_index} (name: '{getattr(deleted_rule, 'name', 'unnamed')}')"
        filtered_rules = [rule for i, rule in enumerate(current_rules) if i != rule_index]

    # Step 3: Update the policy with the filtered rules
    print(f"Deleting rule {deleted_rule_identifier}...")

    # Convert Pydantic models to dicts for the API
    # Use recursive serialization to handle nested Pydantic objects
    rules_as_dicts = [serialize_pydantic(rule) for rule in filtered_rules]

    client.policies.update(
        policy_id=policy_id,
        rules=rules_as_dicts,
        authorization_context=auth_context,
    )

    print(f"Rule deleted successfully! Policy now has {len(filtered_rules)} rule(s)")


if __name__ == "__main__":
    main()
