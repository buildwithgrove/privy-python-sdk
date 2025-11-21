import json
import logging
from typing import Any, Dict, Optional, cast
from typing_extensions import override

import httpx

from .authorization_signatures import get_authorization_signature

logger = logging.getLogger(__name__)


class PrivyHTTPClient(httpx.Client):
    """A custom HTTP client that adds authorization signatures to requests."""

    _authorization_key: Optional[str]

    def __init__(
        self,
        *,
        app_id: str,
        authorization_key: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the client.

        Args:
            app_id: The Privy app ID
            authorization_key: The authorization private key. If not provided, requests will not be signed.
            **kwargs: Additional arguments to pass to httpx.Client
        """
        super().__init__(**kwargs)
        self.app_id = app_id
        self._authorization_key = None

        if authorization_key is not None:
            self._authorization_key = authorization_key

    def _prepare_request(self, request: httpx.Request) -> None:
        """Add authorization signature to the request if authorization_key is set.

        Args:
            request: The request to prepare
        """
        # Methods that require authorization signatures
        SIGNED_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

        # Skip if no authorization key
        if self._authorization_key is None:
            if request.method in SIGNED_METHODS:
                logger.debug(f"Skipping authorization signature for {request.method} {request.url} - no authorization key configured")
            return

        # Skip if not a mutation method
        if request.method not in SIGNED_METHODS:
            return

        # Get the request body
        # IMPORTANT: Read the body content and then restore the stream
        # to avoid consuming it before the actual request is sent
        try:
            body_bytes = request.read()
            # Restore the stream so httpx can read it again when sending
            request.stream = httpx.ByteStream(body_bytes)

            body_str = body_bytes.decode("utf-8")
            if body_str:
                body = json.loads(body_str)
            else:
                body = {}
        except Exception:
            body = {}

        # Extract Privy-specific headers for signature payload
        # According to Privy docs, include headers prefixed with 'privy-'
        privy_headers = {"privy-app-id": self.app_id}
        for header_name, header_value in request.headers.items():
            if header_name.lower().startswith("privy-") and header_name.lower() != "privy-app-id":
                # Don't include the authorization signature itself
                if header_name.lower() != "privy-authorization-signature":
                    privy_headers[header_name.lower()] = header_value

        # Log what we're about to sign
        logger.debug(f"Generating signature for {request.method} {request.url}")
        logger.debug(f"  Headers: {privy_headers}")
        logger.debug(f"  Body keys: {list(body.keys()) if body else '(empty)'}")

        # Generate the signature
        signature = get_authorization_signature(
            url=str(request.url),
            body=cast(Dict[str, Any], body),
            method=request.method,
            headers=privy_headers,
            private_key=self._authorization_key,
        )

        # Add the signature to the request headers
        request.headers["privy-authorization-signature"] = signature
        logger.debug(f"Added authorization signature (length: {len(signature)})")

    @override
    def send(self, request: httpx.Request, **kwargs: Any) -> httpx.Response:
        """Send a request with authorization signature if authorization_key is set.

        Args:
            request: The request to send
            **kwargs: Additional arguments to pass to httpx.Client.send

        Returns:
            The response from the server
        """
        # Capture request body before sending (for logging on error)
        request_body_for_logging = None
        try:
            if hasattr(request, 'content') and request.content:
                request_body_for_logging = request.content.decode('utf-8')
        except Exception:
            pass

        self._prepare_request(request)
        response = super().send(request, **kwargs)

        # Log full request details on authorization errors (401)
        if response.status_code == 401:
            logger.error("=" * 80)
            logger.error("PRIVY AUTHORIZATION ERROR - Full Request Details:")
            logger.error("=" * 80)
            logger.error(f"Method: {request.method}")
            logger.error(f"URL: {request.url}")
            logger.error(f"Headers:")
            for key, value in request.headers.items():
                # Mask sensitive values but show presence
                if key.lower() in ("authorization", "privy-authorization-signature"):
                    logger.error(f"  {key}: {'[PRESENT]' if value else '[MISSING]'} (length: {len(value) if value else 0})")
                else:
                    logger.error(f"  {key}: {value}")

            # Log request body (if captured)
            if request_body_for_logging:
                logger.error(f"Body: {request_body_for_logging}")
            else:
                logger.error("Body: [NOT CAPTURED]")

            # Log response
            logger.error(f"Response Status: {response.status_code}")
            logger.error(f"Response Body: {response.text}")
            logger.error("=" * 80)

        return response
