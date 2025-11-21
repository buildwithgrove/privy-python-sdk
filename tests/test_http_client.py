"""Tests for PrivyHTTPClient authorization signature injection."""

import json
import httpx
import pytest
from unittest.mock import Mock, patch

from privy.lib.http_client import PrivyHTTPClient


class TestPrivyHTTPClient:
    """Test suite for PrivyHTTPClient."""

    def test_request_body_not_consumed(self):
        """Test that reading the body for signature doesn't consume the request stream."""
        # Create client with authorization key
        client = PrivyHTTPClient(
            app_id="test_app",
            authorization_key="dGVzdF9rZXk=",  # base64 "test_key"
        )

        # Create a mock request with a body
        request_body = {"method": "eth_sendTransaction", "params": {"to": "0x123"}}
        request = httpx.Request(
            method="POST",
            url="https://api.privy.io/v1/wallets/wallet_id/rpc",
            json=request_body,
        )

        # Mock the signature generation to avoid crypto operations
        with patch("privy.lib.http_client.get_authorization_signature") as mock_sig:
            mock_sig.return_value = "mock_signature"

            # Prepare the request (this adds the signature header)
            client._prepare_request(request)

            # Verify signature was added
            assert "privy-authorization-signature" in request.headers
            assert request.headers["privy-authorization-signature"] == "mock_signature"

            # Verify the request body can still be read
            body_bytes = request.read()
            assert len(body_bytes) > 0
            assert json.loads(body_bytes) == request_body

            # Verify signature was generated with correct parameters
            mock_sig.assert_called_once()
            call_kwargs = mock_sig.call_args[1]
            assert call_kwargs["method"] == "POST"
            assert call_kwargs["app_id"] == "test_app"
            assert call_kwargs["body"] == request_body

    def test_no_signature_without_authorization_key(self):
        """Test that requests are not signed when authorization_key is not set."""
        client = PrivyHTTPClient(app_id="test_app")

        request = httpx.Request(
            method="POST",
            url="https://api.privy.io/v1/wallets/wallet_id/rpc",
            json={"method": "eth_sendTransaction"},
        )

        # Prepare request without authorization key
        client._prepare_request(request)

        # Verify no signature header was added
        assert "privy-authorization-signature" not in request.headers

    def test_no_signature_for_get_requests(self):
        """Test that GET requests are not signed even with authorization_key."""
        client = PrivyHTTPClient(
            app_id="test_app",
            authorization_key="dGVzdF9rZXk=",
        )

        request = httpx.Request(
            method="GET",
            url="https://api.privy.io/v1/wallets",
        )

        # Prepare GET request
        client._prepare_request(request)

        # Verify no signature header was added
        assert "privy-authorization-signature" not in request.headers

    def test_authorization_key_can_be_updated(self):
        """Test that authorization key can be updated after client creation."""
        client = PrivyHTTPClient(app_id="test_app")

        # Initially no key
        assert client._authorization_key is None

        # Update the key
        client._authorization_key = "dGVzdF9rZXk="
        assert client._authorization_key == "dGVzdF9rZXk="

    def test_empty_body_handled_gracefully(self):
        """Test that requests with empty bodies are handled correctly."""
        client = PrivyHTTPClient(
            app_id="test_app",
            authorization_key="dGVzdF9rZXk=",
        )

        # Create request with no body
        request = httpx.Request(
            method="POST",
            url="https://api.privy.io/v1/wallets",
        )

        with patch("privy.lib.http_client.get_authorization_signature") as mock_sig:
            mock_sig.return_value = "mock_signature"

            # Prepare the request
            client._prepare_request(request)

            # Verify signature was generated with empty body
            call_kwargs = mock_sig.call_args[1]
            assert call_kwargs["body"] == {}
