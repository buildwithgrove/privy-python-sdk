"""Extended Policies resource with AuthorizationContext support.

Extends the base PoliciesResource to support automatic signature generation
via AuthorizationContext for operations that require authorization signatures.
"""

from typing import Any, Dict, Iterable, Optional, Union, List, cast

import httpx

from typing_extensions import Literal

from .authorization_context import AuthorizationContext
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform, strip_not_given
from .._base_client import make_request_options
from ..types import policy_create_params, policy_update_params
from ..types.policy import Policy
from ..resources.policies import (
    PoliciesResource as BasePoliciesResource,
    AsyncPoliciesResource as BaseAsyncPoliciesResource,
)


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

    Args:
        authorization_context: Optional AuthorizationContext for automatic signature generation
        privy_authorization_signature: Manual signature(s), ignored if authorization_context is provided
        request_method: HTTP method (e.g., "POST", "PATCH", "DELETE")
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


class PoliciesResource(BasePoliciesResource):
    """Extended Policies resource with AuthorizationContext support.

    Extends the base PoliciesResource to support automatic signature generation
    via AuthorizationContext for operations that require authorization signatures.
    """

    def add_rule(
        self,
        policy_id: str,
        *,
        name: str,
        method: Literal[
            "eth_sendTransaction",
            "eth_signTransaction",
            "eth_signTypedData_v4",
            "signTransaction",
            "signAndSendTransaction",
            "exportPrivateKey",
            "*",
        ],
        conditions: Iterable[policy_create_params.RuleCondition],
        action: Literal["ALLOW", "DENY"],
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Add a new rule to an existing policy with automatic signature generation.

        This method adds a single rule to a policy without replacing existing rules.
        Requires authorization signatures for security.

        Args:
            policy_id: ID of the policy to add the rule to
            name: Name/description for the rule
            method: RPC method this rule applies to (e.g., "eth_sendTransaction", "*")
            conditions: List of conditions that define when this rule applies.
                Each condition specifies a field, operator, and value to check.
            action: Action to take when conditions match ("ALLOW" or "DENY")
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
            The created rule data

        Example:
            # Using AuthorizationContext (recommended)
            auth_context = (
                AuthorizationContext.builder()
                .add_authorization_private_key("key1")
                .build()
            )

            rule = client.policies.add_rule(
                policy_id="policy_abc123",
                name="Allow transfers to treasury",
                method="eth_sendTransaction",
                conditions=[{
                    "field_source": "ethereum_transaction",
                    "field": "to",
                    "operator": "eq",
                    "value": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
                }],
                action="ALLOW",
                authorization_context=auth_context,
            )

            # Using manual signature
            rule = client.policies.add_rule(
                policy_id="policy_abc123",
                name="Allow transfers to treasury",
                method="eth_sendTransaction",
                conditions=[...],
                action="ALLOW",
                privy_authorization_signature="sig1,sig2",
            )
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")

        # Prepare request body for signature generation
        request_body = {
            "name": name,
            "method": method,
            "conditions": conditions,
            "action": action,
        }

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="POST",
            request_url=f"{self._client.base_url}/v1/policies/{policy_id}/rules",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }

        return self._post(
            f"/v1/policies/{policy_id}/rules",
            body=request_body,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def update(
        self,
        policy_id: str,
        *,
        rules: Iterable[policy_update_params.Rule] | NotGiven = NOT_GIVEN,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Any:
        """Update a policy with automatic signature generation via AuthorizationContext.

        This extended method supports both manual signature passing and automatic
        signature generation via AuthorizationContext.

        Args:
            policy_id: ID of the policy to update
            rules: The rules that apply to each method the policy covers
            authorization_context: AuthorizationContext for automatic signature generation
            privy_authorization_signature: Manual authorization signature(s)
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request

        Returns:
            Updated Policy

        Example:
            # Using AuthorizationContext (recommended)
            auth_context = (
                AuthorizationContext.builder()
                .add_authorization_private_key("key1")
                .build()
            )

            policy = client.policies.update(
                policy_id="policy_id",
                rules=[...],
                authorization_context=auth_context
            )
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")

        # If no authorization_context provided, use parent method
        # This allows the HTTP client's authorization key (set via update_authorization_key) to work
        if authorization_context is None:
            return super().update(
                policy_id=policy_id,
                rules=rules,
                privy_authorization_signature=privy_authorization_signature,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )

        # If authorization_context provided, generate signatures
        request_body = {
            "rules": rules,
        }

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="PATCH",
            request_url=f"{self._client.base_url}/v1/policies/{policy_id}",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }

        return self._patch(
            f"/v1/policies/{policy_id}",
            body=maybe_transform(
                {
                    "rules": rules,
                },
                policy_update_params.PolicyUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=cast(Any, object),
        )

    def delete(
        self,
        policy_id: str,
        *,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Policy:
        """Delete a policy with automatic signature generation via AuthorizationContext.

        Args:
            policy_id: ID of the policy to delete
            authorization_context: AuthorizationContext for automatic signature generation
            privy_authorization_signature: Manual authorization signature(s)
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request

        Example:
            # Using AuthorizationContext (recommended)
            auth_context = (
                AuthorizationContext.builder()
                .add_authorization_private_key("key1")
                .build()
            )

            client.policies.delete(
                policy_id="policy_id",
                authorization_context=auth_context
            )
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")

        # If no authorization_context provided, use parent method
        if authorization_context is None:
            return super().delete(
                policy_id=policy_id,
                privy_authorization_signature=privy_authorization_signature,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )

        # If authorization_context provided, generate signatures
        request_body: Dict[str, Any] = {}

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="DELETE",
            request_url=f"{self._client.base_url}/v1/policies/{policy_id}",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }

        return self._delete(
            f"/v1/policies/{policy_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Policy,
        )


class AsyncPoliciesResource(BaseAsyncPoliciesResource):
    """Extended Async Policies resource with AuthorizationContext support.

    Extends the base AsyncPoliciesResource to support automatic signature generation
    via AuthorizationContext for operations that require authorization signatures.
    """

    async def add_rule(
        self,
        policy_id: str,
        *,
        name: str,
        method: Literal[
            "eth_sendTransaction",
            "eth_signTransaction",
            "eth_signTypedData_v4",
            "signTransaction",
            "signAndSendTransaction",
            "exportPrivateKey",
            "*",
        ],
        conditions: Iterable[policy_create_params.RuleCondition],
        action: Literal["ALLOW", "DENY"],
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Asynchronously add a new rule to an existing policy.

        This method adds a single rule to a policy without replacing existing rules.
        Requires authorization signatures for security.

        Args:
            policy_id: ID of the policy to add the rule to
            name: Name/description for the rule
            method: RPC method this rule applies to
            conditions: List of conditions that define when this rule applies
            action: Action to take when conditions match ("ALLOW" or "DENY")
            authorization_context: AuthorizationContext for automatic signature generation
            privy_authorization_signature: Manual authorization signature(s)
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request

        Returns:
            The created rule data
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")

        # Prepare request body for signature generation
        request_body = {
            "name": name,
            "method": method,
            "conditions": conditions,
            "action": action,
        }

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="POST",
            request_url=f"{self._client.base_url}/v1/policies/{policy_id}/rules",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }

        return await self._post(
            f"/v1/policies/{policy_id}/rules",
            body=request_body,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def update(
        self,
        policy_id: str,
        *,
        rules: Iterable[policy_update_params.Rule] | NotGiven = NOT_GIVEN,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Any:
        """Asynchronously update a policy with automatic signature generation.

        Args:
            policy_id: ID of the policy to update
            rules: The rules that apply to each method the policy covers
            authorization_context: AuthorizationContext for automatic signature generation
            privy_authorization_signature: Manual authorization signature(s)
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request

        Returns:
            Updated Policy
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")

        # If no authorization_context provided, use parent method
        if authorization_context is None:
            return await super().update(
                policy_id=policy_id,
                rules=rules,
                privy_authorization_signature=privy_authorization_signature,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )

        # If authorization_context provided, generate signatures
        request_body = {
            "rules": rules,
        }

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="PATCH",
            request_url=f"{self._client.base_url}/v1/policies/{policy_id}",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }

        return await self._patch(
            f"/v1/policies/{policy_id}",
            body=await async_maybe_transform(
                {
                    "rules": rules,
                },
                policy_update_params.PolicyUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=cast(Any, object),
        )

    async def delete(
        self,
        policy_id: str,
        *,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Policy:
        """Asynchronously delete a policy with automatic signature generation.

        Args:
            policy_id: ID of the policy to delete
            authorization_context: AuthorizationContext for automatic signature generation
            privy_authorization_signature: Manual authorization signature(s)
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request
        """
        if not policy_id:
            raise ValueError(f"Expected a non-empty value for `policy_id` but received {policy_id!r}")

        # If no authorization_context provided, use parent method
        if authorization_context is None:
            return await super().delete(
                policy_id=policy_id,
                privy_authorization_signature=privy_authorization_signature,
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
            )

        # If authorization_context provided, generate signatures
        request_body: Dict[str, Any] = {}

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="DELETE",
            request_url=f"{self._client.base_url}/v1/policies/{policy_id}",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }

        return await self._delete(
            f"/v1/policies/{policy_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Policy,
        )
