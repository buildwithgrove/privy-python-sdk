"""Extended Transactions resource with AuthorizationContext support.

TODO_IN_THIS_PR: Implement authorization_context support for wallet transactions
This should follow the same pattern as key_quorums.py:
1. Extend wallets.transactions.create() method
2. Add authorization_context parameter
3. Use _prepare_authorization_headers() helper from key_quorums.py
4. Support both sync and async variants

Example intended API:
    auth_context = (
        AuthorizationContext.builder()
        .add_authorization_private_key("key1")
        .build()
    )

    response = client.wallets.transactions.create(
        wallet_id="wallet_id",
        chain_type="ethereum",
        transaction={"to": "0x...", "value": "1000000000000000000"},
        authorization_context=auth_context
    )

See: privy/lib/key_quorums.py for reference implementation
"""
