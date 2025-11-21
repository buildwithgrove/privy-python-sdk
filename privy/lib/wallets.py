from typing import Any, List, Union, Optional, Iterable, Dict, cast

import httpx

from typing_extensions import Literal

from .hpke import open, generate_keypair, seal
from .authorization_context import AuthorizationContext
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform, strip_not_given
from .._base_client import make_request_options
from .._models import BaseModel
from ..types.wallet import Wallet
from ..types import wallet_update_params
from ..resources.wallets import (
    WalletsResource as BaseWalletsResource,
    AsyncWalletsResource as BaseAsyncWalletsResource,
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


class DecryptedWalletAuthenticateWithJwtResponse:
    """Response containing the decrypted authorization key and associated wallet information.

    This response contains the decrypted authorization key that can be used directly
    for wallet operations, along with the expiration time and wallet information.
    """

    def __init__(
        self,
        *,
        decrypted_authorization_key: str,
        expires_at: float,
        wallets: List[Any],
    ):
        self.decrypted_authorization_key = decrypted_authorization_key
        self.expires_at = expires_at
        self.wallets = wallets


class WalletImportInitResponse(BaseModel):
    """Response from wallet import initialization containing the encryption public key.

    This response contains the encryption public key that should be used to encrypt
    the wallet's private key before submitting the import.
    """

    encryption_type: str
    """The encryption type (currently only HPKE is supported)."""

    encryption_public_key: str
    """Base64-encoded encryption public key to encrypt the wallet entropy with."""


class WalletsResource(BaseWalletsResource):
    """Extended Wallets resource with AuthorizationContext support.

    Extends the base WalletsResource to support automatic signature generation
    via AuthorizationContext for operations that require authorization signatures.
    """

    def update(
        self,
        wallet_id: str,
        *,
        additional_signers: Iterable[wallet_update_params.AdditionalSigner] | NotGiven = NOT_GIVEN,
        owner: Optional[wallet_update_params.Owner] | NotGiven = NOT_GIVEN,
        owner_id: Optional[str] | NotGiven = NOT_GIVEN,
        policy_ids: List[str] | NotGiven = NOT_GIVEN,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Wallet:
        """Update a wallet with automatic signature generation via AuthorizationContext.

        This extended method supports both manual signature passing and automatic
        signature generation via AuthorizationContext.

        Args:
            wallet_id: ID of the wallet to update
            additional_signers: Additional signers for the wallet
            owner: The P-256 public key of the owner of the wallet. If you provide this,
                do not specify an owner_id as it will be generated automatically.
            owner_id: The key quorum ID to set as the owner of the wallet. If you provide
                this, do not specify an owner.
            policy_ids: New policy IDs to enforce on the wallet. Currently, only one policy
                is supported per wallet.
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
            Updated Wallet

        Example:
            # Using AuthorizationContext (recommended)
            auth_context = (
                AuthorizationContext.builder()
                .add_authorization_private_key("key1")
                .add_authorization_private_key("key2")
                .build()
            )

            wallet = client.wallets.update(
                wallet_id="wallet_id",
                policy_ids=["policy_id"],
                authorization_context=auth_context
            )

            # Using manual signatures
            wallet = client.wallets.update(
                wallet_id="wallet_id",
                policy_ids=["policy_id"],
                privy_authorization_signature="sig1,sig2"
            )
        """
        if not wallet_id:
            raise ValueError(f"Expected a non-empty value for `wallet_id` but received {wallet_id!r}")

        # Prepare request body for signature generation
        request_body = {
            "additional_signers": additional_signers,
            "owner": owner,
            "owner_id": owner_id,
            "policy_ids": policy_ids,
        }

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="PATCH",
            request_url=f"{self._client.base_url}/v1/wallets/{wallet_id}",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }

        return self._patch(
            f"/v1/wallets/{wallet_id}",
            body=maybe_transform(
                {
                    "additional_signers": additional_signers,
                    "owner": owner,
                    "owner_id": owner_id,
                    "policy_ids": policy_ids,
                },
                wallet_update_params.WalletUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Wallet,
        )

    def generate_user_signer(
        self,
        *,
        user_jwt: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> DecryptedWalletAuthenticateWithJwtResponse:
        """Authenticate with a JWT and automatically handle keypair generation and decryption.

        This method performs a complete authentication flow that:
        1. Generates an ephemeral keypair for secure key exchange
        2. Authenticates with the provided JWT
        3. Decrypts the authorization key using the generated keypair

        Args:
            user_jwt: The JWT token for authentication
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            DecryptedWalletAuthenticateWithJwtResponse containing the decrypted authorization key
        """
        # Generate an ephemeral keypair for the exchange
        ephemeral_keypair = generate_keypair()
        encrypted_payload = super().authenticate_with_jwt(
            encryption_type="HPKE",
            recipient_public_key=ephemeral_keypair["public_key"],
            user_jwt=user_jwt,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        decrypted_authorization_key = open(
            private_key=ephemeral_keypair["private_key"],
            encapsulated_key=encrypted_payload.encrypted_authorization_key.encapsulated_key,
            ciphertext=encrypted_payload.encrypted_authorization_key.ciphertext,
        )
        return DecryptedWalletAuthenticateWithJwtResponse(
            decrypted_authorization_key=decrypted_authorization_key["message"],
            expires_at=encrypted_payload.expires_at,
            wallets=encrypted_payload.wallets,
        )

    def import_wallet_init(
        self,
        *,
        address: str,
        chain_type: Literal["ethereum", "solana"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> WalletImportInitResponse:
        """Initialize a wallet import and receive encryption public key.

        This is step 1 of the wallet import process. Use the returned encryption_public_key
        to encrypt the wallet's private key, then call import_wallet_submit() to complete
        the import.

        Args:
            address: The address of the wallet to import
            chain_type: The chain type of the wallet (ethereum or solana)
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            WalletImportInitResponse containing the encryption public key
        """
        return self._post(
            "/v1/wallets/import/init",
            body={
                "address": address,
                "chain_type": chain_type,
                "entropy_type": "private-key",
                "encryption_type": "HPKE",
            },
            options={
                "headers": extra_headers or {},
                "query": extra_query or {},
                "extra_body": extra_body or {},
                "timeout": timeout if timeout is not NOT_GIVEN else NOT_GIVEN,
            },
            cast_to=WalletImportInitResponse,
        )

    def import_wallet_submit(
        self,
        *,
        address: str,
        chain_type: Literal["ethereum", "solana"],
        encapsulated_key: str,
        ciphertext: str,
        owner_id: str,
        policy_ids: Optional[List[str]] = None,
        additional_signers: Optional[List[Any]] = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> Wallet:
        """Submit an encrypted wallet for import.

        This is step 2 of the wallet import process. Use this after calling import_wallet_init()
        and encrypting the private key with the provided encryption public key.

        Args:
            address: The address of the wallet to import
            chain_type: The chain type of the wallet (ethereum or solana)
            encapsulated_key: Base64-encoded encapsulated key from HPKE encryption
            ciphertext: Base64-encoded encrypted private key
            owner_id: The key quorum ID of the owner of the wallet
            policy_ids: Optional list of policy IDs to enforce on the wallet
            additional_signers: Optional list of additional signers for the wallet
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            Wallet object representing the imported wallet
        """
        # TODO_IMPROVE: Add support for owner object in addition to owner_id
        body = {
            "wallet": {
                "address": address,
                "chain_type": chain_type,
                "entropy_type": "private-key",
                "encryption_type": "HPKE",
                "encapsulated_key": encapsulated_key,
                "ciphertext": ciphertext,
            },
            "owner_id": owner_id,
        }

        if policy_ids is not None:
            body["policy_ids"] = policy_ids

        if additional_signers is not None:
            body["additional_signers"] = additional_signers

        return self._post(
            "/v1/wallets/import/submit",
            body=body,
            options={
                "headers": extra_headers or {},
                "query": extra_query or {},
                "extra_body": extra_body or {},
                "timeout": timeout if timeout is not NOT_GIVEN else NOT_GIVEN,
            },
            cast_to=Wallet,
        )

    def import_wallet(
        self,
        *,
        private_key: str,
        address: str,
        chain_type: Literal["ethereum", "solana"],
        owner_id: str,
        policy_ids: Optional[List[str]] = None,
        additional_signers: Optional[List[Any]] = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> Wallet:
        """Import a wallet with automatic encryption handling (recommended).

        This method performs the complete wallet import flow:
        1. Initializes the import to get the encryption public key
        2. Encrypts the private key using HPKE
        3. Submits the encrypted wallet data

        This is the recommended method for importing wallets as it handles all
        security-critical operations automatically.

        Args:
            private_key: The private key as hex string (with or without 0x prefix)
            address: The address of the wallet to import
            chain_type: The chain type of the wallet (ethereum or solana)
            owner_id: The key quorum ID of the owner of the wallet
            policy_ids: Optional list of policy IDs to enforce on the wallet
            additional_signers: Optional list of additional signers for the wallet
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            Wallet object representing the imported wallet
        """
        # TODO: Add support for HD wallets (entropy_type: "hd")

        # Step 1: Initialize import to get encryption public key
        init_response = self.import_wallet_init(
            address=address,
            chain_type=chain_type,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        # Step 2: Convert hex private key to raw bytes
        # Remove 0x prefix if present
        hex_key = private_key[2:] if private_key.startswith("0x") else private_key
        # Convert hex to bytes
        key_bytes = bytes.fromhex(hex_key)

        # Step 3: Encrypt the private key bytes using HPKE
        encrypted = seal(
            public_key=init_response.encryption_public_key,
            message=key_bytes,  # Pass raw bytes for encryption
        )

        # Step 4: Submit the encrypted wallet data
        return self.import_wallet_submit(
            address=address,
            chain_type=chain_type,
            encapsulated_key=encrypted["encapsulated_key"],
            ciphertext=encrypted["ciphertext"],
            owner_id=owner_id,
            policy_ids=policy_ids,
            additional_signers=additional_signers,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )


class AsyncWalletsResource(BaseAsyncWalletsResource):
    """Extended Async Wallets resource with AuthorizationContext support.

    Extends the base AsyncWalletsResource to support automatic signature generation
    via AuthorizationContext for operations that require authorization signatures.
    """

    async def update(
        self,
        wallet_id: str,
        *,
        additional_signers: Iterable[wallet_update_params.AdditionalSigner] | NotGiven = NOT_GIVEN,
        owner: Optional[wallet_update_params.Owner] | NotGiven = NOT_GIVEN,
        owner_id: Optional[str] | NotGiven = NOT_GIVEN,
        policy_ids: List[str] | NotGiven = NOT_GIVEN,
        authorization_context: Optional[AuthorizationContext] = None,
        privy_authorization_signature: str | NotGiven = NOT_GIVEN,
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> Wallet:
        """Asynchronously update a wallet with automatic signature generation.

        This extended method supports both manual signature passing and automatic
        signature generation via AuthorizationContext.

        Args:
            wallet_id: ID of the wallet to update
            additional_signers: Additional signers for the wallet
            owner: The P-256 public key of the owner of the wallet
            owner_id: The key quorum ID to set as the owner of the wallet
            policy_ids: New policy IDs to enforce on the wallet
            authorization_context: AuthorizationContext for automatic signature generation
            privy_authorization_signature: Manual authorization signature(s)
            extra_headers: Send extra headers
            extra_query: Add additional query parameters to the request
            extra_body: Add additional JSON properties to the request
            timeout: Override the client-level default timeout for this request

        Returns:
            Updated Wallet
        """
        if not wallet_id:
            raise ValueError(f"Expected a non-empty value for `wallet_id` but received {wallet_id!r}")

        # Prepare request body for signature generation
        request_body = {
            "additional_signers": additional_signers,
            "owner": owner,
            "owner_id": owner_id,
            "policy_ids": policy_ids,
        }

        # Generate authorization headers
        auth_headers = _prepare_authorization_headers(
            authorization_context=authorization_context,
            privy_authorization_signature=privy_authorization_signature,
            request_method="PATCH",
            request_url=f"{self._client.base_url}/v1/wallets/{wallet_id}",
            request_body=request_body,
            app_id=getattr(self._client, 'app_id', ''),
        )

        extra_headers = {
            **auth_headers,
            **(extra_headers or {}),
        }

        return await self._patch(
            f"/v1/wallets/{wallet_id}",
            body=await async_maybe_transform(
                {
                    "additional_signers": additional_signers,
                    "owner": owner,
                    "owner_id": owner_id,
                    "policy_ids": policy_ids,
                },
                wallet_update_params.WalletUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=Wallet,
        )

    async def generate_user_signer(
        self,
        *,
        user_jwt: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> DecryptedWalletAuthenticateWithJwtResponse:
        """Asynchronously authenticate with a JWT and automatically handle keypair generation and decryption.

        This method provides a safe, all-in-one authentication flow that:
        1. Automatically generates a secure ephemeral keypair for the exchange
        2. Handles the authentication with the provided JWT
        3. Securely decrypts the authorization key using the generated keypair
        4. Returns the decrypted authorization key along with wallet information

        This is the recommended method for authentication as it handles all security-critical
        operations in a single call while maintaining proper key management.

        Args:
            user_jwt: The JWT token for authentication
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            DecryptedWalletAuthenticateWithJwtResponse containing the decrypted authorization key
        """
        # Generate an ephemeral keypair for the exchange
        ephemeral_keypair = generate_keypair()
        encrypted_payload = await super().authenticate_with_jwt(
            encryption_type="HPKE",
            recipient_public_key=ephemeral_keypair["public_key"],
            user_jwt=user_jwt,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
        decrypted_authorization_key = open(
            private_key=ephemeral_keypair["private_key"],
            encapsulated_key=encrypted_payload.encrypted_authorization_key.encapsulated_key,
            ciphertext=encrypted_payload.encrypted_authorization_key.ciphertext,
        )
        return DecryptedWalletAuthenticateWithJwtResponse(
            decrypted_authorization_key=decrypted_authorization_key["message"],
            expires_at=encrypted_payload.expires_at,
            wallets=encrypted_payload.wallets,
        )

    async def import_wallet_init(
        self,
        *,
        address: str,
        chain_type: Literal["ethereum", "solana"],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> WalletImportInitResponse:
        """Asynchronously initialize a wallet import and receive encryption public key.

        This is step 1 of the wallet import process. Use the returned encryption_public_key
        to encrypt the wallet's private key, then call import_wallet_submit() to complete
        the import.

        Args:
            address: The address of the wallet to import
            chain_type: The chain type of the wallet (ethereum or solana)
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            WalletImportInitResponse containing the encryption public key
        """
        return await self._post(
            "/v1/wallets/import/init",
            body={
                "address": address,
                "chain_type": chain_type,
                "entropy_type": "private-key",
                "encryption_type": "HPKE",
            },
            options={
                "headers": extra_headers or {},
                "query": extra_query or {},
                "extra_body": extra_body or {},
                "timeout": timeout if timeout is not NOT_GIVEN else NOT_GIVEN,
            },
            cast_to=WalletImportInitResponse,
        )

    async def import_wallet_submit(
        self,
        *,
        address: str,
        chain_type: Literal["ethereum", "solana"],
        encapsulated_key: str,
        ciphertext: str,
        owner_id: str,
        policy_ids: Optional[List[str]] = None,
        additional_signers: Optional[List[Any]] = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> Wallet:
        """Asynchronously submit an encrypted wallet for import.

        This is step 2 of the wallet import process. Use this after calling import_wallet_init()
        and encrypting the private key with the provided encryption public key.

        Args:
            address: The address of the wallet to import
            chain_type: The chain type of the wallet (ethereum or solana)
            encapsulated_key: Base64-encoded encapsulated key from HPKE encryption
            ciphertext: Base64-encoded encrypted private key
            owner_id: The key quorum ID of the owner of the wallet
            policy_ids: Optional list of policy IDs to enforce on the wallet
            additional_signers: Optional list of additional signers for the wallet
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            Wallet object representing the imported wallet
        """
        # TODO_IMPROVE: Add support for owner object in addition to owner_id
        body = {
            "wallet": {
                "address": address,
                "chain_type": chain_type,
                "entropy_type": "private-key",
                "encryption_type": "HPKE",
                "encapsulated_key": encapsulated_key,
                "ciphertext": ciphertext,
            },
            "owner_id": owner_id,
        }

        if policy_ids is not None:
            body["policy_ids"] = policy_ids

        if additional_signers is not None:
            body["additional_signers"] = additional_signers

        return await self._post(
            "/v1/wallets/import/submit",
            body=body,
            options={
                "headers": extra_headers or {},
                "query": extra_query or {},
                "extra_body": extra_body or {},
                "timeout": timeout if timeout is not NOT_GIVEN else NOT_GIVEN,
            },
            cast_to=Wallet,
        )

    async def import_wallet(
        self,
        *,
        private_key: str,
        address: str,
        chain_type: Literal["ethereum", "solana"],
        owner_id: str,
        policy_ids: Optional[List[str]] = None,
        additional_signers: Optional[List[Any]] = None,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Optional[Headers] = None,
        extra_query: Optional[Query] = None,
        extra_body: Optional[Body] = None,
        timeout: Union[float, httpx.Timeout, None, NotGiven] = NOT_GIVEN,
    ) -> Wallet:
        """Asynchronously import a wallet with automatic encryption handling (recommended).

        This method performs the complete wallet import flow:
        1. Initializes the import to get the encryption public key
        2. Encrypts the private key using HPKE
        3. Submits the encrypted wallet data

        This is the recommended method for importing wallets as it handles all
        security-critical operations automatically.

        Args:
            private_key: The private key as hex string (with or without 0x prefix)
            address: The address of the wallet to import
            chain_type: The chain type of the wallet (ethereum or solana)
            owner_id: The key quorum ID of the owner of the wallet
            policy_ids: Optional list of policy IDs to enforce on the wallet
            additional_signers: Optional list of additional signers for the wallet
            extra_headers: Optional additional headers for the request
            extra_query: Optional additional query parameters
            extra_body: Optional additional body parameters
            timeout: Optional timeout for the request

        Returns:
            Wallet object representing the imported wallet
        """
        # TODO: Add support for HD wallets (entropy_type: "hd")

        # Step 1: Initialize import to get encryption public key
        init_response = await self.import_wallet_init(
            address=address,
            chain_type=chain_type,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )

        # Step 2: Convert hex private key to raw bytes
        # Remove 0x prefix if present
        hex_key = private_key[2:] if private_key.startswith("0x") else private_key
        # Convert hex to bytes
        key_bytes = bytes.fromhex(hex_key)

        # Step 3: Encrypt the private key bytes using HPKE
        encrypted = seal(
            public_key=init_response.encryption_public_key,
            message=key_bytes,  # Pass raw bytes for encryption
        )

        # Step 4: Submit the encrypted wallet data
        return await self.import_wallet_submit(
            address=address,
            chain_type=chain_type,
            encapsulated_key=encrypted["encapsulated_key"],
            ciphertext=encrypted["ciphertext"],
            owner_id=owner_id,
            policy_ids=policy_ids,
            additional_signers=additional_signers,
            extra_headers=extra_headers,
            extra_query=extra_query,
            extra_body=extra_body,
            timeout=timeout,
        )
