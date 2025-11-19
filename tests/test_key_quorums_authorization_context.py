"""Tests for KeyQuorums resource with AuthorizationContext integration."""

import pytest
from unittest.mock import Mock, patch
from privy import PrivyAPI, AsyncPrivyAPI
from privy.lib import AuthorizationContext


class TestKeyQuorumsWithAuthorizationContext:
    """Test suite for KeyQuorums resource with AuthorizationContext."""

    def test_update_with_authorization_context(self):
        """Test key quorum update with authorization_context parameter."""
        # Create client
        client = PrivyAPI(app_id="test_app", app_secret="test_secret")

        # Create authorization context with custom signer (to avoid needing real keys)
        def custom_signer(method, url, body, app_id):
            assert method == "PATCH"
            assert "key_quorums" in url
            assert app_id == "test_app"
            return {"signature": f"sig1_for_{body['public_keys'][0]}", "signer_public_key": None}

        auth_context = (
            AuthorizationContext.builder()
            .set_custom_sign_function(custom_signer)
            .build()
        )

        # Mock the _patch method to verify it's called with correct signatures
        with patch.object(client.key_quorums, '_patch') as mock_patch:
            mock_patch.return_value = Mock(id="quorum_123")

            # Call update with authorization_context
            client.key_quorums.update(
                key_quorum_id="quorum_123",
                public_keys=["pubkey1", "pubkey2"],
                authorization_threshold=2,
                authorization_context=auth_context,
            )

            # Verify _patch was called
            assert mock_patch.called
            call_kwargs = mock_patch.call_args[1]

            # Verify signature was included in headers
            assert 'options' in call_kwargs
            headers = call_kwargs['options']['headers']
            assert 'privy-authorization-signature' in headers
            assert headers['privy-authorization-signature'] == "sig1_for_pubkey1"

    def test_update_with_multiple_signatures(self):
        """Test key quorum update generates multiple signatures correctly."""
        client = PrivyAPI(app_id="test_app", app_secret="test_secret")

        # Create authorization context with multiple signers
        def signer1(method, url, body, app_id):
            return {"signature": "sig1", "signer_public_key": None}

        auth_context = (
            AuthorizationContext.builder()
            .set_custom_sign_function(signer1)
            .add_signature("sig2", None)
            .build()
        )

        with patch.object(client.key_quorums, '_patch') as mock_patch:
            mock_patch.return_value = Mock(id="quorum_123")

            client.key_quorums.update(
                key_quorum_id="quorum_123",
                public_keys=["pubkey1", "pubkey2"],
                authorization_context=auth_context,
            )

            # Verify signatures are comma-separated
            call_kwargs = mock_patch.call_args[1]
            headers = call_kwargs['options']['headers']
            sig = headers['privy-authorization-signature']
            assert sig == "sig1,sig2"

    def test_delete_with_authorization_context(self):
        """Test key quorum delete with authorization_context parameter."""
        client = PrivyAPI(app_id="test_app", app_secret="test_secret")

        def custom_signer(method, url, body, app_id):
            assert method == "DELETE"
            assert body == {}  # DELETE has empty body
            return {"signature": "delete_sig", "signer_public_key": None}

        auth_context = (
            AuthorizationContext.builder()
            .set_custom_sign_function(custom_signer)
            .build()
        )

        with patch.object(client.key_quorums, '_delete') as mock_delete:
            mock_delete.return_value = Mock(id="quorum_123")

            client.key_quorums.delete(
                key_quorum_id="quorum_123",
                authorization_context=auth_context,
            )

            assert mock_delete.called
            call_kwargs = mock_delete.call_args[1]
            headers = call_kwargs['options']['headers']
            assert headers['privy-authorization-signature'] == "delete_sig"

    def test_manual_signature_takes_precedence_without_context(self):
        """Test that manual signature works when no authorization_context is provided."""
        client = PrivyAPI(app_id="test_app", app_secret="test_secret")

        with patch.object(client.key_quorums, '_patch') as mock_patch:
            mock_patch.return_value = Mock(id="quorum_123")

            client.key_quorums.update(
                key_quorum_id="quorum_123",
                public_keys=["pubkey1"],
                privy_authorization_signature="manual_sig",
            )

            call_kwargs = mock_patch.call_args[1]
            headers = call_kwargs['options']['headers']
            assert headers['privy-authorization-signature'] == "manual_sig"

    def test_authorization_context_overrides_manual_signature(self):
        """Test that authorization_context takes precedence over manual signature."""
        client = PrivyAPI(app_id="test_app", app_secret="test_secret")

        auth_context = (
            AuthorizationContext.builder()
            .add_signature("context_sig")
            .build()
        )

        with patch.object(client.key_quorums, '_patch') as mock_patch:
            mock_patch.return_value = Mock(id="quorum_123")

            client.key_quorums.update(
                key_quorum_id="quorum_123",
                public_keys=["pubkey1"],
                authorization_context=auth_context,
                privy_authorization_signature="manual_sig",  # Should be ignored
            )

            call_kwargs = mock_patch.call_args[1]
            headers = call_kwargs['options']['headers']
            assert headers['privy-authorization-signature'] == "context_sig"

    def test_create_still_works_without_authorization_context(self):
        """Test that create() method still works (no authorization_context needed)."""
        client = PrivyAPI(app_id="test_app", app_secret="test_secret")

        with patch.object(client.key_quorums, '_post') as mock_post:
            mock_post.return_value = Mock(id="quorum_123")

            # create() doesn't need signatures
            result = client.key_quorums.create(
                public_keys=["pubkey1", "pubkey2"],
                authorization_threshold=2,
            )

            assert mock_post.called
            assert result.id == "quorum_123"


class TestAsyncKeyQuorumsWithAuthorizationContext:
    """Test suite for AsyncKeyQuorums resource with AuthorizationContext."""

    @pytest.mark.asyncio
    async def test_async_update_with_authorization_context(self):
        """Test async key quorum update with authorization_context parameter."""
        client = AsyncPrivyAPI(app_id="test_app", app_secret="test_secret")

        def custom_signer(method, url, body, app_id):
            return {"signature": "async_sig", "signer_public_key": None}

        auth_context = (
            AuthorizationContext.builder()
            .set_custom_sign_function(custom_signer)
            .build()
        )

        with patch.object(client.key_quorums, '_patch') as mock_patch:
            # Make the mock return a coroutine
            async def mock_patch_coro(*args, **kwargs):
                return Mock(id="quorum_123")

            mock_patch.return_value = mock_patch_coro()

            await client.key_quorums.update(
                key_quorum_id="quorum_123",
                public_keys=["pubkey1", "pubkey2"],
                authorization_context=auth_context,
            )

            assert mock_patch.called
            call_kwargs = mock_patch.call_args[1]
            headers = call_kwargs['options']['headers']
            assert headers['privy-authorization-signature'] == "async_sig"

    @pytest.mark.asyncio
    async def test_async_delete_with_authorization_context(self):
        """Test async key quorum delete with authorization_context parameter."""
        client = AsyncPrivyAPI(app_id="test_app", app_secret="test_secret")

        auth_context = (
            AuthorizationContext.builder()
            .add_signature("async_delete_sig")
            .build()
        )

        with patch.object(client.key_quorums, '_delete') as mock_delete:
            async def mock_delete_coro(*args, **kwargs):
                return Mock(id="quorum_123")

            mock_delete.return_value = mock_delete_coro()

            await client.key_quorums.delete(
                key_quorum_id="quorum_123",
                authorization_context=auth_context,
            )

            assert mock_delete.called
            call_kwargs = mock_delete.call_args[1]
            headers = call_kwargs['options']['headers']
            assert headers['privy-authorization-signature'] == "async_delete_sig"


class TestKeyQuorumsResourceType:
    """Test that the correct resource type is being used."""

    def test_sync_client_uses_extended_resource(self):
        """Verify sync client uses extended KeyQuorumsResource."""
        from privy.lib.key_quorums import KeyQuorumsResource

        client = PrivyAPI(app_id="test_app", app_secret="test_secret")
        assert isinstance(client.key_quorums, KeyQuorumsResource)

    def test_async_client_uses_extended_resource(self):
        """Verify async client uses extended AsyncKeyQuorumsResource."""
        from privy.lib.key_quorums import AsyncKeyQuorumsResource

        client = AsyncPrivyAPI(app_id="test_app", app_secret="test_secret")
        assert isinstance(client.key_quorums, AsyncKeyQuorumsResource)
