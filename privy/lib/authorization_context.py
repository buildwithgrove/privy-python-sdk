"""Authorization context for signing Privy API requests.

This module provides an abstraction similar to the Java SDK's AuthorizationContext,
enabling automatic request signing through various methods:
- Authorization private keys
- User JWTs
- Custom signing functions
- Pre-computed signatures
"""

from __future__ import annotations

import base64
from typing import Any, Callable, Dict, List, Optional, Union
from typing_extensions import Protocol, Self, TypedDict

from .authorization_signatures import get_authorization_signature


class SignatureResult(TypedDict):
    """Result of a signature operation."""

    signature: str
    signer_public_key: Optional[str]


class CustomSignFunction(Protocol):
    """Protocol for custom signing functions.

    Custom signing functions allow you to implement signing logic in a separate service
    (e.g., KMS, HSM) or with custom business logic.

    TODO_IMPROVE: Add support for async custom sign functions
    This would enable async KMS integrations but requires:
    1. New AsyncCustomSignFunction protocol
    2. Async-aware generate_signatures() method
    3. Type checking to determine sync vs async function
    Consider this for a future enhancement when async KMS is needed.
    """

    def __call__(
        self,
        request_method: str,
        request_url: str,
        request_body: Dict[str, Any],
        app_id: str,
    ) -> SignatureResult:
        """Sign a request and return the signature.

        Args:
            request_method: HTTP method (e.g., "POST", "GET")
            request_url: Full URL of the request
            request_body: Request body as a dictionary
            app_id: Privy app ID

        Returns:
            SignatureResult containing:
                - signature: Base64-encoded signature
                - signer_public_key: Optional public key used for signing
        """
        ...


class AuthorizationContext:
    """Context for authorizing Privy API requests with automatic signature generation.

    The AuthorizationContext enables server-side request signing through multiple methods:

    1. Authorization keys - Direct P256 signatures using private keys
    2. User JWTs - Request user signing keys and compute P256 signatures
    3. Custom signing function - Delegate signing to external services (KMS, HSM)
    4. Pre-computed signatures - Include signatures computed separately

    Example:
        # Using authorization keys
        context = AuthorizationContext.builder()
            .add_authorization_private_key("base64_encoded_key")
            .build()

        # Using user JWTs
        context = AuthorizationContext.builder()
            .add_user_jwt("user_jwt_token")
            .build()

        # Using custom signing function
        def custom_signer(method, url, body, app_id):
            # Custom signing logic (e.g., call KMS)
            return {"signature": "...", "signer_public_key": None}

        context = AuthorizationContext.builder()
            .set_custom_sign_function(custom_signer)
            .build()

        # Using pre-computed signatures
        context = AuthorizationContext.builder()
            .add_signature("base64_signature", "base64_public_key")
            .build()

        # Pass context to SDK methods that require signing
        response = client.wallets.transactions.create(
            wallet_id="wallet_id",
            chain_type="ethereum",
            transaction={...},
            authorization_context=context
        )
    """

    def __init__(
        self,
        authorization_private_keys: Optional[List[str]] = None,
        user_jwts: Optional[List[str]] = None,
        custom_sign_function: Optional[CustomSignFunction] = None,
        signatures: Optional[List[SignatureResult]] = None,
    ):
        """Initialize an AuthorizationContext.

        Note: Use AuthorizationContext.builder() for a more ergonomic API.

        Args:
            authorization_private_keys: List of authorization private keys for signing
            user_jwts: List of user JWT tokens for user-based signing
            custom_sign_function: Custom function to compute signatures
            signatures: List of pre-computed signatures
        """
        self._authorization_private_keys = authorization_private_keys or []
        self._user_jwts = user_jwts or []
        self._custom_sign_function = custom_sign_function
        self._signatures = signatures or []

    @staticmethod
    def builder() -> AuthorizationContextBuilder:
        """Create a new builder for constructing an AuthorizationContext.

        Returns:
            AuthorizationContextBuilder instance
        """
        return AuthorizationContextBuilder()

    def generate_signatures(
        self,
        request_method: str,
        request_url: str,
        request_body: Dict[str, Any],
        app_id: str,
    ) -> List[str]:
        """Generate all signatures for the given request.

        This method computes signatures based on all signing methods configured:
        - Authorization private keys: Direct ECDSA P-256 signatures
        - User JWTs: Request signing keys and compute signatures (TODO: implement)
        - Custom sign function: Delegate to custom signing logic
        - Pre-computed signatures: Return as-is

        Args:
            request_method: HTTP method (e.g., "POST", "PUT")
            request_url: Full URL of the request
            request_body: Request body as a dictionary
            app_id: Privy app ID

        Returns:
            List of base64-encoded signatures
        """
        all_signatures: List[str] = []

        # 1. Generate signatures from authorization private keys
        for private_key in self._authorization_private_keys:
            signature = get_authorization_signature(
                url=request_url,
                body=request_body,
                method=request_method,
                app_id=app_id,
                private_key=private_key,
            )
            all_signatures.append(signature)

        # 2. Generate signatures from user JWTs
        # TODO_IN_THIS_PR: Implement user JWT-based signing
        # This requires:
        # - Calling the API to exchange JWT for signing keys
        # - Using the returned keys to sign the request
        if self._user_jwts:
            raise NotImplementedError(
                "User JWT-based signing is not yet implemented. "
                "Please use authorization_private_keys or custom_sign_function instead."
            )

        # 3. Use custom signing function if provided
        if self._custom_sign_function:
            result = self._custom_sign_function(
                request_method,
                request_url,
                request_body,
                app_id,
            )
            all_signatures.append(result["signature"])

        # 4. Include pre-computed signatures
        for sig_result in self._signatures:
            all_signatures.append(sig_result["signature"])

        return all_signatures

    @property
    def has_signing_methods(self) -> bool:
        """Check if any signing methods are configured.

        Returns:
            True if at least one signing method is configured
        """
        return (
            len(self._authorization_private_keys) > 0
            or len(self._user_jwts) > 0
            or self._custom_sign_function is not None
            or len(self._signatures) > 0
        )


class AuthorizationContextBuilder:
    """Builder for constructing AuthorizationContext instances.

    Provides a fluent API for building authorization contexts with multiple
    signing methods.

    Example:
        context = (
            AuthorizationContext.builder()
            .add_authorization_private_key("key1")
            .add_authorization_private_key("key2")
            .add_user_jwt("jwt_token")
            .build()
        )
    """

    def __init__(self):
        """Initialize a new builder."""
        self._authorization_private_keys: List[str] = []
        self._user_jwts: List[str] = []
        self._custom_sign_function: Optional[CustomSignFunction] = None
        self._signatures: List[SignatureResult] = []

    def add_authorization_private_key(self, private_key: str) -> Self:
        """Add an authorization private key for signing.

        The private key will be used to compute ECDSA P-256 signatures over requests.

        Args:
            private_key: Base64-encoded private key

        Returns:
            Self for method chaining
        """
        self._authorization_private_keys.append(private_key)
        return self

    def add_user_jwt(self, jwt: str) -> Self:
        """Add a user JWT for user-based signing.

        The SDK will request user signing keys given the JWT and compute P256 signatures.

        Note: This feature is not yet implemented.

        Args:
            jwt: User JWT token

        Returns:
            Self for method chaining
        """
        self._user_jwts.append(jwt)
        return self

    def set_custom_sign_function(self, sign_function: CustomSignFunction) -> Self:
        """Set a custom signing function.

        Use this when signing logic needs to occur in a separate service (e.g., KMS, HSM)
        or requires custom business logic.

        Args:
            sign_function: Function that takes (method, url, body, app_id) and returns SignatureResult

        Returns:
            Self for method chaining
        """
        self._custom_sign_function = sign_function
        return self

    def add_signature(
        self,
        signature: str,
        signer_public_key: Optional[str] = None,
    ) -> Self:
        """Add a pre-computed signature.

        Use this if you compute signatures separately from calling the SDK.

        Args:
            signature: Base64-encoded signature
            signer_public_key: Optional public key used to generate the signature

        Returns:
            Self for method chaining
        """
        self._signatures.append(
            {
                "signature": signature,
                "signer_public_key": signer_public_key,
            }
        )
        return self

    def build(self) -> AuthorizationContext:
        """Build the AuthorizationContext.

        Returns:
            Configured AuthorizationContext instance
        """
        return AuthorizationContext(
            authorization_private_keys=self._authorization_private_keys,
            user_jwts=self._user_jwts,
            custom_sign_function=self._custom_sign_function,
            signatures=self._signatures,
        )
