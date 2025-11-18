# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["WalletAuthenticateWithJwtParams"]


class WalletAuthenticateWithJwtParams(TypedDict, total=False):
    encryption_type: Required[Literal["HPKE"]]
    """The encryption type for the authentication response.

    Currently only supports HPKE.
    """

    recipient_public_key: Required[str]
    """Base64-encoded public key of the recipient who will decrypt the session key.

    This key must be generated securely and kept confidential.
    """

    user_jwt: Required[str]
    """The user's JWT, to be used to authenticate the user."""
