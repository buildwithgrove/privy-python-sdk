# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, Annotated, TypeAlias, TypedDict

from .._utils import PropertyInfo

__all__ = [
    "WalletRpcParams",
    "EthSignTransaction",
    "EthSignTransactionParams",
    "EthSignTransactionParamsTransaction",
    "EthSendTransaction",
    "EthSendTransactionParams",
    "EthSendTransactionParamsTransaction",
    "PersonalSign",
    "PersonalSignParams",
    "EthSignTypedDataV4",
    "EthSignTypedDataV4Params",
    "EthSignTypedDataV4ParamsTypedData",
    "EthSignTypedDataV4ParamsTypedDataType",
    "Secp256k1Sign",
    "Secp256k1SignParams",
    "SignTransaction",
    "SignTransactionParams",
    "SignAndSendTransaction",
    "SignAndSendTransactionParams",
    "SignMessage",
    "SignMessageParams",
]


class EthSignTransaction(TypedDict, total=False):
    method: Required[Literal["eth_signTransaction"]]

    params: Required[EthSignTransactionParams]

    address: str

    chain_type: Literal["ethereum"]

    privy_authorization_signature: Annotated[str, PropertyInfo(alias="privy-authorization-signature")]
    """Request authorization signature.

    If multiple signatures are required, they should be comma separated.
    """


_EthSignTransactionParamsTransactionReservedKeywords = TypedDict(
    "_EthSignTransactionParamsTransactionReservedKeywords",
    {
        "from": str,
    },
    total=False,
)


class EthSignTransactionParamsTransaction(_EthSignTransactionParamsTransactionReservedKeywords, total=False):
    chain_id: Union[str, int]

    data: str

    gas_limit: Union[str, int]

    gas_price: Union[str, int]

    max_fee_per_gas: Union[str, int]

    max_priority_fee_per_gas: Union[str, int]

    nonce: Union[str, int]

    to: str

    type: Literal[0, 1, 2]

    value: Union[str, int]


class EthSignTransactionParams(TypedDict, total=False):
    transaction: Required[EthSignTransactionParamsTransaction]


class EthSendTransaction(TypedDict, total=False):
    caip2: Required[str]

    method: Required[Literal["eth_sendTransaction"]]

    params: Required[EthSendTransactionParams]

    address: str

    chain_type: Literal["ethereum"]

    privy_authorization_signature: Annotated[str, PropertyInfo(alias="privy-authorization-signature")]
    """Request authorization signature.

    If multiple signatures are required, they should be comma separated.
    """


_EthSendTransactionParamsTransactionReservedKeywords = TypedDict(
    "_EthSendTransactionParamsTransactionReservedKeywords",
    {
        "from": str,
    },
    total=False,
)


class EthSendTransactionParamsTransaction(_EthSendTransactionParamsTransactionReservedKeywords, total=False):
    chain_id: Union[str, int]

    data: str

    gas_limit: Union[str, int]

    gas_price: Union[str, int]

    max_fee_per_gas: Union[str, int]

    max_priority_fee_per_gas: Union[str, int]

    nonce: Union[str, int]

    to: str

    type: Literal[0, 1, 2]

    value: Union[str, int]


class EthSendTransactionParams(TypedDict, total=False):
    transaction: Required[EthSendTransactionParamsTransaction]


class PersonalSign(TypedDict, total=False):
    method: Required[Literal["personal_sign"]]

    params: Required[PersonalSignParams]

    address: str

    chain_type: Literal["ethereum"]

    privy_authorization_signature: Annotated[str, PropertyInfo(alias="privy-authorization-signature")]
    """Request authorization signature.

    If multiple signatures are required, they should be comma separated.
    """


class PersonalSignParams(TypedDict, total=False):
    encoding: Required[Literal["utf-8", "hex"]]

    message: Required[str]


class EthSignTypedDataV4(TypedDict, total=False):
    method: Required[Literal["eth_signTypedData_v4"]]

    params: Required[EthSignTypedDataV4Params]

    address: str

    chain_type: Literal["ethereum"]

    privy_authorization_signature: Annotated[str, PropertyInfo(alias="privy-authorization-signature")]
    """Request authorization signature.

    If multiple signatures are required, they should be comma separated.
    """


class EthSignTypedDataV4ParamsTypedDataType(TypedDict, total=False):
    name: Required[str]

    type: Required[str]


class EthSignTypedDataV4ParamsTypedData(TypedDict, total=False):
    domain: Required[Dict[str, Optional[object]]]

    message: Required[Dict[str, Optional[object]]]

    primary_type: Required[str]

    types: Required[Dict[str, Iterable[EthSignTypedDataV4ParamsTypedDataType]]]


class EthSignTypedDataV4Params(TypedDict, total=False):
    typed_data: Required[EthSignTypedDataV4ParamsTypedData]


class Secp256k1Sign(TypedDict, total=False):
    method: Required[Literal["secp256k1_sign"]]

    params: Required[Secp256k1SignParams]

    address: str

    chain_type: Literal["ethereum"]

    privy_authorization_signature: Annotated[str, PropertyInfo(alias="privy-authorization-signature")]
    """Request authorization signature.

    If multiple signatures are required, they should be comma separated.
    """


class Secp256k1SignParams(TypedDict, total=False):
    hash: object


class SignTransaction(TypedDict, total=False):
    method: Required[Literal["signTransaction"]]

    params: Required[SignTransactionParams]

    address: str

    chain_type: Literal["solana"]

    privy_authorization_signature: Annotated[str, PropertyInfo(alias="privy-authorization-signature")]
    """Request authorization signature.

    If multiple signatures are required, they should be comma separated.
    """


class SignTransactionParams(TypedDict, total=False):
    encoding: Required[Literal["base64"]]

    transaction: Required[str]


class SignAndSendTransaction(TypedDict, total=False):
    caip2: Required[str]

    method: Required[Literal["signAndSendTransaction"]]

    params: Required[SignAndSendTransactionParams]

    address: str

    chain_type: Literal["solana"]

    privy_authorization_signature: Annotated[str, PropertyInfo(alias="privy-authorization-signature")]
    """Request authorization signature.

    If multiple signatures are required, they should be comma separated.
    """


class SignAndSendTransactionParams(TypedDict, total=False):
    encoding: Required[Literal["base64"]]

    transaction: Required[str]


class SignMessage(TypedDict, total=False):
    method: Required[Literal["signMessage"]]

    params: Required[SignMessageParams]

    address: str

    chain_type: Literal["solana"]

    privy_authorization_signature: Annotated[str, PropertyInfo(alias="privy-authorization-signature")]
    """Request authorization signature.

    If multiple signatures are required, they should be comma separated.
    """


class SignMessageParams(TypedDict, total=False):
    encoding: Required[Literal["base64"]]

    message: Required[str]


WalletRpcParams: TypeAlias = Union[
    EthSignTransaction,
    EthSendTransaction,
    PersonalSign,
    EthSignTypedDataV4,
    Secp256k1Sign,
    SignTransaction,
    SignAndSendTransaction,
    SignMessage,
]
