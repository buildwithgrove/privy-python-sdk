# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Union, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel

__all__ = [
    "WalletRpcResponse",
    "SignTransaction",
    "SignTransactionData",
    "SignAndSendTransaction",
    "SignAndSendTransactionData",
    "SignAndSendTransactionError",
    "SignMessage",
    "SignMessageData",
    "EthSignTransaction",
    "EthSignTransactionData",
    "EthSendTransaction",
    "EthSendTransactionData",
    "EthSendTransactionError",
    "PersonalSign",
    "PersonalSignData",
    "EthSignTypedDataV4",
    "EthSignTypedDataV4Data",
    "Secp256k1Sign",
    "Secp256k1SignData",
]


class SignTransactionData(BaseModel):
    encoding: Literal["base64"]

    signed_transaction: str


class SignTransaction(BaseModel):
    data: SignTransactionData

    method: Literal["signTransaction"]


class SignAndSendTransactionData(BaseModel):
    caip2: str

    hash: str

    transaction_id: Optional[str] = None


class SignAndSendTransactionError(BaseModel):
    code: str

    message: str


class SignAndSendTransaction(BaseModel):
    method: Literal["signAndSendTransaction"]

    data: Optional[SignAndSendTransactionData] = None

    error: Optional[SignAndSendTransactionError] = None


class SignMessageData(BaseModel):
    encoding: Literal["base64"]

    signature: str


class SignMessage(BaseModel):
    data: SignMessageData

    method: Literal["signMessage"]


class EthSignTransactionData(BaseModel):
    encoding: Literal["rlp"]

    signed_transaction: str


class EthSignTransaction(BaseModel):
    data: EthSignTransactionData

    method: Literal["eth_signTransaction"]


class EthSendTransactionData(BaseModel):
    caip2: str

    hash: str

    transaction_id: Optional[str] = None


class EthSendTransactionError(BaseModel):
    code: str

    message: str


class EthSendTransaction(BaseModel):
    method: Literal["eth_sendTransaction"]

    data: Optional[EthSendTransactionData] = None

    error: Optional[EthSendTransactionError] = None


class PersonalSignData(BaseModel):
    encoding: Literal["hex"]

    signature: str


class PersonalSign(BaseModel):
    data: PersonalSignData

    method: Literal["personal_sign"]


class EthSignTypedDataV4Data(BaseModel):
    encoding: Literal["hex"]

    signature: str


class EthSignTypedDataV4(BaseModel):
    data: EthSignTypedDataV4Data

    method: Literal["eth_signTypedData_v4"]


class Secp256k1SignData(BaseModel):
    encoding: Literal["hex"]

    signature: str


class Secp256k1Sign(BaseModel):
    data: Secp256k1SignData

    method: Literal["secp256k1_sign"]


WalletRpcResponse: TypeAlias = Union[
    SignTransaction,
    SignAndSendTransaction,
    SignMessage,
    EthSignTransaction,
    EthSendTransaction,
    PersonalSign,
    EthSignTypedDataV4,
    Secp256k1Sign,
]
