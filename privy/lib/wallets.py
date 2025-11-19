from typing import Any, List, Union, Optional

import httpx

from typing_extensions import Literal

from .hpke import open, generate_keypair, seal
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._models import BaseModel
from ..types.wallet import Wallet
from ..resources.wallets import (
    WalletsResource as BaseWalletsResource,
    AsyncWalletsResource as BaseAsyncWalletsResource,
)


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

        # Step 3: Submit the encrypted wallet data
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
