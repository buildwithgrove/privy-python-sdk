"""Unit tests for wallet import functionality.

These tests focus on the custom import_wallet functions in lib/wallets.py,
ensuring proper HPKE encryption integration and function flow.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from privy import PrivyAPI, AsyncPrivyAPI
from privy.lib.wallets import WalletImportInitResponse
from privy.types.wallet import Wallet


class TestImportWalletInit:
    """Test import_wallet_init() function."""

    def test_import_wallet_init_success(self, httpx_mock):
        """Test successful wallet import initialization."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/init",
            json={
                "encryption_type": "HPKE",
                "encryption_public_key": "BDAZLOIdTaPycEYkgG0MvCzbIKJLli/yWkAV5yCa9yOsZ4JsrLweA5MnP8YIiY4k/RRzC+APhhO+P+Hoz/rt7Go="
            }
        )

        client = PrivyAPI(app_id="test_app_id", app_secret="test_secret")

        result = client.wallets.import_wallet_init(
            address="0xF1DBff66C993EE895C8cb176c30b07A559d76496",
            chain_type="ethereum"
        )

        assert isinstance(result, WalletImportInitResponse)
        assert result.encryption_type == "HPKE"
        assert result.encryption_public_key == "BDAZLOIdTaPycEYkgG0MvCzbIKJLli/yWkAV5yCa9yOsZ4JsrLweA5MnP8YIiY4k/RRzC+APhhO+P+Hoz/rt7Go="

    def test_import_wallet_init_sends_correct_payload(self, httpx_mock):
        """Test that init sends the correct request payload."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/init",
            json={
                "encryption_type": "HPKE",
                "encryption_public_key": "test_key"
            }
        )

        client = PrivyAPI(app_id="test_app_id", app_secret="test_secret")

        client.wallets.import_wallet_init(
            address="0xABC123",
            chain_type="solana"
        )

        request = httpx_mock.get_request()
        assert request.method == "POST"

        # Verify request body contains correct fields
        import json
        body = json.loads(request.content)
        assert body["address"] == "0xABC123"
        assert body["chain_type"] == "solana"
        assert body["entropy_type"] == "private-key"
        assert body["encryption_type"] == "HPKE"


class TestImportWalletSubmit:
    """Test import_wallet_submit() function."""

    def test_import_wallet_submit_success(self, httpx_mock):
        """Test successful wallet import submission."""
        # Mock the API response
        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/submit",
            json={
                "id": "wallet_123",
                "address": "0xF1DBff66C993EE895C8cb176c30b07A559d76496",
                "chain_type": "ethereum",
                "policy_ids": [],
                "additional_signers": [],
                "owner_id": "owner_123",
                "created_at": 1741834854578,
                "exported_at": None,
                "imported_at": 1741834854578
            }
        )

        client = PrivyAPI(app_id="test_app_id", app_secret="test_secret")

        result = client.wallets.import_wallet_submit(
            address="0xF1DBff66C993EE895C8cb176c30b07A559d76496",
            chain_type="ethereum",
            encapsulated_key="test_encapsulated_key",
            ciphertext="test_ciphertext",
            owner_id="owner_123"
        )

        assert isinstance(result, Wallet)
        assert result.id == "wallet_123"
        assert result.address == "0xF1DBff66C993EE895C8cb176c30b07A559d76496"
        assert result.chain_type == "ethereum"
        assert result.owner_id == "owner_123"

    def test_import_wallet_submit_with_policies(self, httpx_mock):
        """Test wallet import with policy IDs."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/submit",
            json={
                "id": "wallet_123",
                "address": "0xABC",
                "chain_type": "ethereum",
                "policy_ids": ["policy_1"],
                "additional_signers": [],
                "owner_id": "owner_123",
                "created_at": 1741834854578,
                "exported_at": None,
                "imported_at": None
            }
        )

        client = PrivyAPI(app_id="test_app_id", app_secret="test_secret")

        result = client.wallets.import_wallet_submit(
            address="0xABC",
            chain_type="ethereum",
            encapsulated_key="key",
            ciphertext="cipher",
            owner_id="owner_123",
            policy_ids=["policy_1"]
        )

        assert result.policy_ids == ["policy_1"]

        # Verify request payload
        request = httpx_mock.get_request()
        import json
        body = json.loads(request.content)
        assert body["policy_ids"] == ["policy_1"]


class TestImportWallet:
    """Test the complete import_wallet() wrapper function."""

    @patch('privy.lib.wallets.seal')
    def test_import_wallet_complete_flow(self, mock_seal, httpx_mock):
        """Test that import_wallet() orchestrates init + encrypt + submit correctly."""
        # Mock HPKE seal function
        mock_seal.return_value = {
            "encapsulated_key": "mock_encapsulated_key",
            "ciphertext": "mock_ciphertext"
        }

        # Mock init response
        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/init",
            json={
                "encryption_type": "HPKE",
                "encryption_public_key": "mock_public_key"
            }
        )

        # Mock submit response
        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/submit",
            json={
                "id": "wallet_123",
                "address": "0xF1DBff66C993EE895C8cb176c30b07A559d76496",
                "chain_type": "ethereum",
                "policy_ids": [],
                "additional_signers": [],
                "owner_id": "owner_123",
                "created_at": 1741834854578,
                "exported_at": None,
                "imported_at": 1741834854578
            }
        )

        client = PrivyAPI(app_id="test_app_id", app_secret="test_secret")

        result = client.wallets.import_wallet(
            private_key="0x1234567890abcdef",
            address="0xF1DBff66C993EE895C8cb176c30b07A559d76496",
            chain_type="ethereum",
            owner_id="owner_123"
        )

        # Verify seal was called with correct parameters
        mock_seal.assert_called_once_with(
            public_key="mock_public_key",
            message="0x1234567890abcdef"
        )

        # Verify result
        assert isinstance(result, Wallet)
        assert result.id == "wallet_123"
        assert result.imported_at == 1741834854578

    @patch('privy.lib.wallets.seal')
    def test_import_wallet_hpke_encryption(self, mock_seal, httpx_mock):
        """Test that import_wallet() properly integrates HPKE encryption."""
        mock_seal.return_value = {
            "encapsulated_key": "encrypted_key_123",
            "ciphertext": "encrypted_cipher_456"
        }

        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/init",
            json={
                "encryption_type": "HPKE",
                "encryption_public_key": "server_public_key"
            }
        )

        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/submit",
            json={
                "id": "wallet_123",
                "address": "0xABC",
                "chain_type": "ethereum",
                "policy_ids": [],
                "additional_signers": [],
                "owner_id": "owner_123",
                "created_at": 1741834854578,
                "exported_at": None,
                "imported_at": None
            }
        )

        client = PrivyAPI(app_id="test_app_id", app_secret="test_secret")

        client.wallets.import_wallet(
            private_key="my_secret_key",
            address="0xABC",
            chain_type="ethereum",
            owner_id="owner_123"
        )

        # Verify seal was called with the encryption public key from init
        mock_seal.assert_called_once_with(
            public_key="server_public_key",
            message="my_secret_key"
        )

        # Verify the encrypted data was sent to submit endpoint
        requests = httpx_mock.get_requests()
        submit_request = requests[1]  # Second request is submit
        import json
        submit_body = json.loads(submit_request.content)

        assert submit_body["wallet"]["encapsulated_key"] == "encrypted_key_123"
        assert submit_body["wallet"]["ciphertext"] == "encrypted_cipher_456"


class TestAsyncImportWallet:
    """Test async variants of import wallet functions."""

    async def test_async_import_wallet_init(self, httpx_mock):
        """Test async import_wallet_init() function."""
        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/init",
            json={
                "encryption_type": "HPKE",
                "encryption_public_key": "async_public_key"
            }
        )

        client = AsyncPrivyAPI(app_id="test_app_id", app_secret="test_secret")

        result = await client.wallets.import_wallet_init(
            address="0xABC",
            chain_type="ethereum"
        )

        assert isinstance(result, WalletImportInitResponse)
        assert result.encryption_public_key == "async_public_key"

    @patch('privy.lib.wallets.seal')
    async def test_async_import_wallet_complete_flow(self, mock_seal, httpx_mock):
        """Test async import_wallet() complete flow."""
        mock_seal.return_value = {
            "encapsulated_key": "async_key",
            "ciphertext": "async_cipher"
        }

        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/init",
            json={
                "encryption_type": "HPKE",
                "encryption_public_key": "async_pub_key"
            }
        )

        httpx_mock.add_response(
            method="POST",
            url="https://api.privy.io/v1/wallets/import/submit",
            json={
                "id": "async_wallet_123",
                "address": "0xASYNC",
                "chain_type": "solana",
                "policy_ids": [],
                "additional_signers": [],
                "owner_id": "async_owner",
                "created_at": 1741834854578,
                "exported_at": None,
                "imported_at": None
            }
        )

        client = AsyncPrivyAPI(app_id="test_app_id", app_secret="test_secret")

        result = await client.wallets.import_wallet(
            private_key="async_private_key",
            address="0xASYNC",
            chain_type="solana",
            owner_id="async_owner"
        )

        assert isinstance(result, Wallet)
        assert result.id == "async_wallet_123"
        assert result.chain_type == "solana"

        # Verify seal was called correctly
        mock_seal.assert_called_once_with(
            public_key="async_pub_key",
            message="async_private_key"
        )
