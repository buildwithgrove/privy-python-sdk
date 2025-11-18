from typing import List, Union, Optional

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._base_client import make_request_options
from ..resources.users import (
    UsersResource as BaseUsersResource,
    AsyncUsersResource as BaseAsyncUsersResource,
)
from ..types.wallet_create_wallets_with_recovery_params import (
    Wallet,
    RecoveryUserLinkedAccount,
)
from ..types.wallet_create_wallets_with_recovery_response import (
    WalletCreateWalletsWithRecoveryResponse,
)


class UsersResource(BaseUsersResource):
    def create_with_jwt_auth(
        self,
        *,
        jwt_subject_id: str,
        wallets: List[Wallet],
        additional_linked_accounts: Optional[List[RecoveryUserLinkedAccount]] = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> WalletCreateWalletsWithRecoveryResponse:
        """Create a wallet with a simplified interface.

        This method provides a simplified interface for creating wallets that:
        1. Sets up a primary signer with the provided jwt_subject_id
        2. Creates a recovery user with the custom JWT account and any additional linked accounts
        3. Creates the specified wallet(s)

        Args:
            jwt_subject_id: The JWT subject ID of the user
            wallets: List of wallet configurations (e.g. [{"chain_type": "ethereum"}])
            additional_linked_accounts: Optional list of additional linked accounts to add to the recovery user
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            WalletCreateWalletsWithRecoveryResponse containing the created wallets and recovery user ID
        """
        # Prepare linked accounts, ensuring custom JWT account is included
        linked_accounts: List[RecoveryUserLinkedAccount] = [{"custom_user_id": jwt_subject_id, "type": "custom_auth"}]

        # Add any additional linked accounts if provided
        if additional_linked_accounts:
            # Check if any additional account conflicts with the custom JWT account
            for account in additional_linked_accounts:
                if account.get("type") == "custom_auth":
                    raise ValueError("Custom JWT account should only be specified in jwt_subject_id")
            linked_accounts.extend(additional_linked_accounts)

        # TODO: figure out if we can use the underlying method instead (client.wallets.create_wallets_with_recovery)
        return self._post(
            "/v1/wallets_with_recovery",
            body=maybe_transform(
                {
                    "primary_signer": {"subject_id": jwt_subject_id},
                    "recovery_user": {"linked_accounts": linked_accounts},
                    "wallets": wallets,
                },
                "wallet_create_wallets_with_recovery_params",
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=WalletCreateWalletsWithRecoveryResponse,
        )


class AsyncUsersResource(BaseAsyncUsersResource):
    async def create_with_jwt_auth(
        self,
        *,
        jwt_subject_id: str,
        wallets: List[Wallet],
        additional_linked_accounts: Optional[List[RecoveryUserLinkedAccount]] = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> WalletCreateWalletsWithRecoveryResponse:
        """Create a wallet with a simplified interface.

        This method provides a simplified interface for creating wallets that:
        1. Sets up a primary signer with the provided jwt_subject_id
        2. Creates a recovery user with the custom JWT account and any additional linked accounts
        3. Creates the specified wallet(s)

        Args:
            jwt_subject_id: The JWT subject ID of the user
            wallets: List of wallet configurations (e.g. [{"chain_type": "ethereum"}])
            additional_linked_accounts: Optional list of additional linked accounts to add to the recovery user
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            WalletCreateWalletsWithRecoveryResponse containing the created wallets and recovery user ID
        """
        # Prepare linked accounts, ensuring custom JWT account is included
        linked_accounts: List[RecoveryUserLinkedAccount] = [{"custom_user_id": jwt_subject_id, "type": "custom_auth"}]

        # Add any additional linked accounts if provided
        if additional_linked_accounts:
            # Check if any additional account conflicts with the custom JWT account
            for account in additional_linked_accounts:
                if account.get("type") == "custom_auth":
                    raise ValueError("Custom JWT account should only be specified in jwt_subject_id")
            linked_accounts.extend(additional_linked_accounts)

        # TODO: figure out if we can use the underlying method instead (client.wallets.create_wallets_with_recovery)
        return await self._post(
            "/v1/wallets_with_recovery",
            body=await async_maybe_transform(
                {
                    "primary_signer": {"subject_id": jwt_subject_id},
                    "recovery_user": {"linked_accounts": linked_accounts},
                    "wallets": wallets,
                },
                "wallet_create_wallets_with_recovery_params",
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            ),
            cast_to=WalletCreateWalletsWithRecoveryResponse,
        )
