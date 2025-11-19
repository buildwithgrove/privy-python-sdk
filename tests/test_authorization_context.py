"""Tests for AuthorizationContext."""

import pytest
from privy.lib import AuthorizationContext, SignatureResult


class TestAuthorizationContext:
    """Test suite for AuthorizationContext."""

    def test_builder_with_authorization_keys(self):
        """Test building context with authorization private keys."""
        context = (
            AuthorizationContext.builder()
            .add_authorization_private_key("key1")
            .add_authorization_private_key("key2")
            .build()
        )

        assert context.has_signing_methods
        assert len(context._authorization_private_keys) == 2
        assert context._authorization_private_keys[0] == "key1"
        assert context._authorization_private_keys[1] == "key2"

    def test_builder_strips_wallet_auth_prefix(self):
        """Test that wallet-auth: prefix is stripped from keys."""
        context = (
            AuthorizationContext.builder()
            .add_authorization_private_key("wallet-auth:test_key")
            .build()
        )

        assert context._authorization_private_keys[0] == "test_key"

    def test_builder_with_custom_sign_function(self):
        """Test building context with custom signing function."""

        def custom_signer(method, url, body, app_id):
            return {"signature": "custom_sig", "signer_public_key": None}

        context = (
            AuthorizationContext.builder()
            .set_custom_sign_function(custom_signer)
            .build()
        )

        assert context.has_signing_methods
        assert context._custom_sign_function is not None

    def test_builder_with_precomputed_signatures(self):
        """Test building context with pre-computed signatures."""
        context = (
            AuthorizationContext.builder()
            .add_signature("sig1", "pubkey1")
            .add_signature("sig2", None)
            .build()
        )

        assert context.has_signing_methods
        assert len(context._signatures) == 2
        assert context._signatures[0]["signature"] == "sig1"
        assert context._signatures[0]["signer_public_key"] == "pubkey1"
        assert context._signatures[1]["signature"] == "sig2"
        assert context._signatures[1]["signer_public_key"] is None

    def test_builder_with_user_jwt(self):
        """Test building context with user JWT."""
        context = (
            AuthorizationContext.builder()
            .add_user_jwt("jwt_token")
            .build()
        )

        assert context.has_signing_methods
        assert len(context._user_jwts) == 1
        assert context._user_jwts[0] == "jwt_token"

    def test_empty_context_has_no_signing_methods(self):
        """Test that empty context reports no signing methods."""
        context = AuthorizationContext.builder().build()

        assert not context.has_signing_methods

    def test_generate_signatures_with_custom_function(self):
        """Test signature generation with custom function."""

        def custom_signer(method, url, body, app_id):
            return {"signature": f"sig_{method}_{app_id}", "signer_public_key": None}

        context = (
            AuthorizationContext.builder()
            .set_custom_sign_function(custom_signer)
            .build()
        )

        signatures = context.generate_signatures(
            request_method="POST",
            request_url="https://api.privy.io/test",
            request_body={},
            app_id="test_app",
        )

        assert len(signatures) == 1
        assert signatures[0] == "sig_POST_test_app"

    def test_generate_signatures_with_precomputed(self):
        """Test signature generation with pre-computed signatures."""
        context = (
            AuthorizationContext.builder()
            .add_signature("precomputed_sig1")
            .add_signature("precomputed_sig2")
            .build()
        )

        signatures = context.generate_signatures(
            request_method="POST",
            request_url="https://api.privy.io/test",
            request_body={},
            app_id="test_app",
        )

        assert len(signatures) == 2
        assert signatures[0] == "precomputed_sig1"
        assert signatures[1] == "precomputed_sig2"

    def test_generate_signatures_with_user_jwt_not_implemented(self):
        """Test that user JWT signing raises NotImplementedError."""
        context = (
            AuthorizationContext.builder()
            .add_user_jwt("jwt_token")
            .build()
        )

        with pytest.raises(NotImplementedError, match="User JWT-based signing is not yet implemented"):
            context.generate_signatures(
                request_method="POST",
                request_url="https://api.privy.io/test",
                request_body={},
                app_id="test_app",
            )

    def test_combined_signing_methods(self):
        """Test combining multiple signing methods."""

        def custom_signer(method, url, body, app_id):
            return {"signature": "custom_sig", "signer_public_key": None}

        context = (
            AuthorizationContext.builder()
            .set_custom_sign_function(custom_signer)
            .add_signature("precomputed_sig")
            .build()
        )

        signatures = context.generate_signatures(
            request_method="POST",
            request_url="https://api.privy.io/test",
            request_body={},
            app_id="test_app",
        )

        # Should have 2 signatures: 1 from custom function, 1 pre-computed
        assert len(signatures) == 2
        assert "custom_sig" in signatures
        assert "precomputed_sig" in signatures

    def test_direct_instantiation(self):
        """Test direct instantiation (not using builder)."""
        context = AuthorizationContext(
            authorization_private_keys=["key1", "key2"],
            signatures=[{"signature": "sig1", "signer_public_key": None}],
        )

        assert context.has_signing_methods
        assert len(context._authorization_private_keys) == 2
        assert len(context._signatures) == 1
