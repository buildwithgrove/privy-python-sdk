"""Extended Policies resource with AuthorizationContext support.

TODO_IN_THIS_PR: Implement authorization_context support for policy operations
This should follow the same pattern as key_quorums.py:
1. Extend policies.update() and/or policies.delete() methods
2. Add authorization_context parameter
3. Use _prepare_authorization_headers() helper (consider extracting to shared module)
4. Support both sync and async variants

Example intended API:
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("key1")
        .build()
    )

    response = client.policies.update(
        policy_id="policy_id",
        ...policy_params,
        authorization_context=auth_context
    )

See: privy/lib/key_quorums.py for reference implementation
"""
