# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "UserCreateParams",
    "LinkedAccount",
    "LinkedAccountWallet",
    "LinkedAccountEmail",
    "LinkedAccountPhone",
    "LinkedAccountGoogle",
    "LinkedAccountTwitter",
    "LinkedAccountDiscord",
    "LinkedAccountGitHub",
    "LinkedAccountSpotify",
    "LinkedAccountInstagram",
    "LinkedAccountTiktok",
    "LinkedAccountApple",
    "LinkedAccountLinkedIn",
    "LinkedAccountFarcaster",
    "LinkedAccountTelegram",
    "LinkedAccountCustomJwt",
]


class UserCreateParams(TypedDict, total=False):
    linked_accounts: Required[Iterable[LinkedAccount]]

    create_ethereum_smart_wallet: bool
    """Create a smart wallet. Requires create_ethereum_wallet to also be true."""

    create_ethereum_wallet: bool
    """Create an Ethereum embedded wallet.

    Cannot be used with create_n_ethereum_wallets.
    """

    create_n_ethereum_wallets: float
    """Number of Ethereum embedded wallets to pregenerate.

    Cannot be used with create_ethereum_wallet.
    """

    create_solana_wallet: bool
    """Create a Solana embedded wallet."""

    custom_metadata: Dict[str, Union[str, float, bool]]
    """Custom metadata associated with the user."""


class LinkedAccountWallet(TypedDict, total=False):
    address: Required[str]

    chain_type: Required[Literal["ethereum", "solana"]]

    type: Required[Literal["wallet"]]


class LinkedAccountEmail(TypedDict, total=False):
    address: Required[str]

    type: Required[Literal["email"]]


class LinkedAccountPhone(TypedDict, total=False):
    number: Required[str]

    type: Required[Literal["phone"]]


class LinkedAccountGoogle(TypedDict, total=False):
    email: Required[str]

    name: Required[str]

    subject: Required[str]

    type: Required[Literal["google_oauth"]]


class LinkedAccountTwitter(TypedDict, total=False):
    name: Required[str]

    subject: Required[str]

    type: Required[Literal["twitter_oauth"]]

    username: Required[str]

    profile_picture_url: str


class LinkedAccountDiscord(TypedDict, total=False):
    subject: Required[str]

    type: Required[Literal["discord_oauth"]]

    username: Required[str]

    email: str


class LinkedAccountGitHub(TypedDict, total=False):
    subject: Required[str]

    type: Required[Literal["github_oauth"]]

    username: Required[str]

    email: str

    name: str


class LinkedAccountSpotify(TypedDict, total=False):
    subject: Required[str]

    type: Required[Literal["spotify_oauth"]]

    email: str

    name: str


class LinkedAccountInstagram(TypedDict, total=False):
    subject: Required[str]

    type: Required[Literal["instagram_oauth"]]

    username: Required[str]


class LinkedAccountTiktok(TypedDict, total=False):
    name: Required[Optional[str]]

    subject: Required[str]

    type: Required[Literal["tiktok_oauth"]]

    username: Required[str]


class LinkedAccountApple(TypedDict, total=False):
    subject: Required[str]

    type: Required[Literal["apple_oauth"]]

    email: str


class LinkedAccountLinkedIn(TypedDict, total=False):
    subject: Required[str]

    type: Required[Literal["linkedin_oauth"]]

    email: str

    name: str

    vanity_name: Annotated[str, PropertyInfo(alias="vanityName")]


class LinkedAccountFarcaster(TypedDict, total=False):
    fid: Required[int]

    owner_address: Required[str]

    type: Required[Literal["farcaster"]]

    bio: str

    display_name: str

    homepage_url: str

    profile_picture_url: str

    username: str


class LinkedAccountTelegram(TypedDict, total=False):
    telegram_user_id: Required[str]

    type: Required[Literal["telegram"]]

    first_name: str

    last_name: str

    photo_url: str

    username: str


class LinkedAccountCustomJwt(TypedDict, total=False):
    custom_user_id: Required[str]

    type: Required[Literal["custom_auth"]]


LinkedAccount: TypeAlias = Union[
    LinkedAccountWallet,
    LinkedAccountEmail,
    LinkedAccountPhone,
    LinkedAccountGoogle,
    LinkedAccountTwitter,
    LinkedAccountDiscord,
    LinkedAccountGitHub,
    LinkedAccountSpotify,
    LinkedAccountInstagram,
    LinkedAccountTiktok,
    LinkedAccountApple,
    LinkedAccountLinkedIn,
    LinkedAccountFarcaster,
    LinkedAccountTelegram,
    LinkedAccountCustomJwt,
]
