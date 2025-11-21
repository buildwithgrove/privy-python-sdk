import json
import base64
from typing import Any, Dict, cast

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey


def canonicalize(obj: Any) -> str:
    """Simple JSON canonicalization function.

    Sorts dictionary keys and ensures consistent formatting.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def get_authorization_signature(
    url: str,
    body: Dict[str, Any],
    method: str,
    private_key: str,
    app_id: str | None = None,
    headers: Dict[str, str] | None = None,
) -> str:
    """Generate authorization signature for Privy API requests using ECDSA P-256.

    Args:
        url: The URL of the request
        body: The request body
        method: HTTP method (POST, PUT, PATCH, DELETE)
        private_key: Base64-encoded PKCS#8 EC private key
        app_id: The Privy app ID (deprecated - use headers instead)
        headers: Privy-specific headers to include in signature payload

    Returns:
        The base64-encoded signature
    """
    # Build headers dict - support both old (app_id) and new (headers) API
    if headers is None:
        if app_id is None:
            raise ValueError("Either app_id or headers must be provided")
        headers = {"privy-app-id": app_id}

    # Construct the payload
    payload = {
        "version": 1,
        "method": method,
        "url": url,
        "body": body,
        "headers": headers,
    }

    # Serialize the payload to JSON
    serialized_payload = canonicalize(payload)

    # Create ECDSA P-256 signing key from private key
    private_key_pem = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"

    # Load the private key from PEM format
    loaded_private_key = cast(
        EllipticCurvePrivateKey, serialization.load_pem_private_key(data=private_key_pem.encode("utf-8"), password=None)
    )

    # Sign the message using ECDSA with SHA-256
    signature = loaded_private_key.sign(
        serialized_payload.encode("utf-8"), signature_algorithm=ec.ECDSA(hashes.SHA256())
    )

    # Convert the signature to base64 for easy transmission
    return base64.b64encode(signature).decode("utf-8")
