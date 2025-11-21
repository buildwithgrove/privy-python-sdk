"""Extended KeyQuorums resource with AuthorizationContext support."""

from typing import Any, Dict, List, Optional, Union

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform, strip_not_given
from .._base_client import make_request_options
from ..resources.key_quorums import (
    KeyQuorumsResource as BaseKeyQuorumsResource,
    AsyncKeyQuorumsResource as BaseAsyncKeyQuorumsResource,
)
from ..types import key_quorum_update_params
from ..types.key_quorum import KeyQuorum
from .authorization_context import AuthorizationContext


def _prepare_authorization_headers(
    authorization_context: Optional[AuthorizationContext],
    privy_authorization_signature: str | NotGiven,
    request_method: str,
    request_url: str,
    request_body: Dict[str, Any],
    app_id: str,
) -> Dict[str, str]:
    """Generate authorization headers from context or manual signature.

    This helper handles the common pattern of generating signatures from an
    AuthorizationContext or using a manually provided signature.

    TODO_IMPROVE: Extract to shared module for reuse
    Once we extend more resources (transactions, policies), consider moving
    this to a shared location like privy.lib._resource_helpers to avoid duplication.

    Args:
        authorization_context: Optional AuthorizationContext for automatic signature generation
        privy_authorization_signature: Manual signature(s), ignored if authorization_context is provided
        request_method: HTTP method (e.g., "PATCH", "DELETE")
        request_url: Full URL of the request
        request_body: Request body as a dictionary
        app_id: Privy app ID

    Returns:
        Dictionary with authorization signature header (may be empty if no signature)
    """
    if authorization_context is not None:
        signatures = authorization_context.generate_signatures(
            request_method=request_method,
            request_url=request_url,
            request_body=request_body,
            app_id=app_id,
        )
        privy_authorization_signature = ",".join(signatures)

    return strip_not_given({"privy-authorization-signature": privy_authorization_signature})


class KeyQuorumsResource(BaseKeyQuorumsResource):
    """Extended KeyQuorums resource with AuthorizationContext support.

    Extends the base KeyQuorumsResource to support automatic signature generation
    via AuthorizationContext for operations that require authorization signatures.
    """

    def update(
        self,
        key_quorum_id: str,
        *,
        public_keys: List[str],
        authorization_threshold: float | NotGiven = NOT_GIVEN,
        display_name: str | NotGiven = NOT_GIVEN,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KeyQuorum:
        """Update a key quorum by key quorum ID with automatic signature generation.

        This extended method supports both manual signature passing and automatic
        signature generation via AuthorizationContext.

        Args:
            key_quorum_id: The ID of the key quorum to update
            public_keys: List of public keys for the quorum
            authorization_threshold: Number of signatures required (e.g., 2 for 2-of-3)
            display_name: Optional display name for the quorum
            authorization_context: AuthorizationContext for automatic signature generation.
                If provided, signatures will be generated and included automatically.
            privy_authorization_signature: Manual authorization signature(s). If multiple
                signatures are required, they should be comma separated. This is ignored
                if authorization_context is provided.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds

        Returns:
            Updated KeyQuorum

        Example:
            # Using AuthorizationContext (recommended)
            auth_context = (
                AuthorizationContext.builder()
                .add_authorization_private_key("key1")
                .add_authorization_private_key("key2")
                .build()
            )

            key_quorum = client.key_quorums.update(
                key_quorum_id="quorum_id",
                public_keys=["pubkey1", "pubkey2"],
                authorization_threshold=2,
                authorization_context=auth_context
            )

            # Using manual signatures
            key_quorum = client.key_quorums.update(
                key_quorum_id="quorum_id",
                public_keys=["pubkey1", "pubkey2"],
                privy_authorization_signature="sig1,sig2"
            )
        """
        if not key_quorum_id:
            raise ValueError(f"Expected a non-empty value for `key_quorum_id` but received {key_quorum_id!r}")

        # Prepare request body for signature generation
        request_body = {
            "public_keys": public_keys,
            "authorization_threshold": authorization_threshold,
            "display_name": display_name,
        }

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="PATCH",
            request_url=f"{self._client.base_url}/v1/key_quorums/{key_quorum_id}",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }
        return self._patch(
            f"/v1/key_quorums/{key_quorum_id}",
            body=maybe_transform(
                {
                    "public_keys": public_keys,
                    "authorization_threshold": authorization_threshold,
                    "display_name": display_name,
                },
                key_quorum_update_params.KeyQuorumUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyQuorum,
        )

    def delete(
        self,
        key_quorum_id: str,
        *,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KeyQuorum:
        """Delete a key quorum by key quorum ID with automatic signature generation.

        This extended method supports both manual signature passing and automatic
        signature generation via AuthorizationContext.

        Args:
            key_quorum_id: The ID of the key quorum to delete
            authorization_context: AuthorizationContext for automatic signature generation.
                If provided, signatures will be generated and included automatically.
            privy_authorization_signature: Manual authorization signature(s). If multiple
                signatures are required, they should be comma separated. This is ignored
                if authorization_context is provided.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds

        Returns:
            Deleted KeyQuorum

        Example:
            # Using AuthorizationContext (recommended)
            auth_context = (
                AuthorizationContext.builder()
                .add_authorization_private_key("key1")
                .add_authorization_private_key("key2")
                .build()
            )

            key_quorum = client.key_quorums.delete(
                key_quorum_id="quorum_id",
                authorization_context=auth_context
            )

            # Using manual signatures
            key_quorum = client.key_quorums.delete(
                key_quorum_id="quorum_id",
                privy_authorization_signature="sig1,sig2"
            )
        """
        if not key_quorum_id:
            raise ValueError(f"Expected a non-empty value for `key_quorum_id` but received {key_quorum_id!r}")

        # Generate authorization headers (DELETE has empty body)
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="DELETE",
            request_url=f"{self._client.base_url}/v1/key_quorums/{key_quorum_id}",
            request_body={},
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }
        return self._delete(
            f"/v1/key_quorums/{key_quorum_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyQuorum,
        )


class AsyncKeyQuorumsResource(BaseAsyncKeyQuorumsResource):
    """Extended AsyncKeyQuorums resource with AuthorizationContext support.

    Extends the base AsyncKeyQuorumsResource to support automatic signature generation
    via AuthorizationContext for operations that require authorization signatures.
    """

    async def update(
        self,
        key_quorum_id: str,
        *,
        public_keys: List[str],
        authorization_threshold: float | NotGiven = NOT_GIVEN,
        display_name: str | NotGiven = NOT_GIVEN,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KeyQuorum:
        """Update a key quorum by key quorum ID with automatic signature generation.

        This extended method supports both manual signature passing and automatic
        signature generation via AuthorizationContext.

        Args:
            key_quorum_id: The ID of the key quorum to update
            public_keys: List of public keys for the quorum
            authorization_threshold: Number of signatures required (e.g., 2 for 2-of-3)
            display_name: Optional display name for the quorum
            authorization_context: AuthorizationContext for automatic signature generation.
                If provided, signatures will be generated and included automatically.
            privy_authorization_signature: Manual authorization signature(s). If multiple
                signatures are required, they should be comma separated. This is ignored
                if authorization_context is provided.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds

        Returns:
            Updated KeyQuorum

        Example:
            # Using AuthorizationContext (recommended)
            auth_context = (
                AuthorizationContext.builder()
                .add_authorization_private_key("key1")
                .add_authorization_private_key("key2")
                .build()
            )

            key_quorum = await client.key_quorums.update(
                key_quorum_id="quorum_id",
                public_keys=["pubkey1", "pubkey2"],
                authorization_threshold=2,
                authorization_context=auth_context
            )

            # Using manual signatures
            key_quorum = await client.key_quorums.update(
                key_quorum_id="quorum_id",
                public_keys=["pubkey1", "pubkey2"],
                privy_authorization_signature="sig1,sig2"
            )
        """
        if not key_quorum_id:
            raise ValueError(f"Expected a non-empty value for `key_quorum_id` but received {key_quorum_id!r}")

        # Prepare request body for signature generation
        request_body = {
            "public_keys": public_keys,
            "authorization_threshold": authorization_threshold,
            "display_name": display_name,
        }

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="PATCH",
            request_url=f"{self._client.base_url}/v1/key_quorums/{key_quorum_id}",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }
        return await self._patch(
            f"/v1/key_quorums/{key_quorum_id}",
            body=await async_maybe_transform(
                {
                    "public_keys": public_keys,
                    "authorization_threshold": authorization_threshold,
                    "display_name": display_name,
                },
                key_quorum_update_params.KeyQuorumUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyQuorum,
        )

    async def delete(
        self,
        key_quorum_id: str,
        *,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KeyQuorum:
        """Delete a key quorum by key quorum ID with automatic signature generation.

        This extended method supports both manual signature passing and automatic
        signature generation via AuthorizationContext.

        Args:
            key_quorum_id: The ID of the key quorum to delete
            authorization_context: AuthorizationContext for automatic signature generation.
                If provided, signatures will be generated and included automatically.
            privy_authorization_signature: Manual authorization signature(s). If multiple
                signatures are required, they should be comma separated. This is ignored
                if authorization_context is provided.
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request, in seconds

        Returns:
            Deleted KeyQuorum

        Example:
            # Using AuthorizationContext (recommended)
            auth_context = (
                AuthorizationContext.builder()
                .add_authorization_private_key("key1")
                .add_authorization_private_key("key2")
                .build()
            )

            key_quorum = await client.key_quorums.delete(
                key_quorum_id="quorum_id",
                authorization_context=auth_context
            )

            # Using manual signatures
            key_quorum = await client.key_quorums.delete(
                key_quorum_id="quorum_id",
                privy_authorization_signature="sig1,sig2"
            )
        """
        if not key_quorum_id:
            raise ValueError(f"Expected a non-empty value for `key_quorum_id` but received {key_quorum_id!r}")

        # Generate authorization headers (DELETE has empty body)
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="DELETE",
            request_url=f"{self._client.base_url}/v1/key_quorums/{key_quorum_id}",
            request_body={},
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }
        return await self._delete(
            f"/v1/key_quorums/{key_quorum_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KeyQuorum,
        )
