# api/byteship.py
#
# Byteship adapter for video upload and webhook handling.
# Client is initialized via init_byteship(app) in extensions.py.

import hashlib
import hmac
import logging
import time

from byteship import ByteshipClient, Visibility
from byteship.client import DEFAULT_BASE_URL

logger = logging.getLogger(__name__)

_MAX_UPLOAD_BYTES = 200 * 1024 * 1024  # matches Gemini review's 200MB limit

_client = None
_webhook_secret = None


def init_client(api_key, webhook_secret=None):
    global _client, _webhook_secret
    _client = ByteshipClient(api_key=api_key)
    _webhook_secret = webhook_secret

    if not webhook_secret:
        logger.warning("Byteship webhook secret is not set — /webhooks/byteship will reject every call")


def get_client():
    if _client is None:
        raise RuntimeError("Byteship client not initialized — call init_client() first")
    return _client


def generate_upload_url(scenario_id, teacher_id):
    """
    Mint a short-lived Byteship upload token for direct client-side upload.

    Byteship's create_upload_token() has no free-form context/metadata
    field (that only exists on server-side upload() calls, which we don't
    use here). So teacher_id/scenario_id are encoded into the folder path
    itself, and parsed back out of the file's `path` when the webhook
    fires (see parse_context_from_path below).

    The client uses the returned token directly against Byteship's own
    upload endpoints — our server never touches the file bytes.
    """
    client = get_client()

    folder = f"teachers/{teacher_id}/scenarios/{scenario_id}"

    response = client.create_upload_token(
        folder=folder,
        visibility=Visibility.PUBLIC,
        max_upload_bytes=_MAX_UPLOAD_BYTES,
        expires_in_seconds=15 * 60,
    )

    return {
        "upload_token": response.upload_token.token,
        # Browser flow: POST here with "Authorization: Bearer <upload_token>"
        # to open an upload session (SDK: create_upload -> POST /v1/uploads).
        "upload_url": f"{DEFAULT_BASE_URL}/v1/uploads",
        "expires_at": response.upload_token.expires_at.isoformat(),
        "folder": folder,
        "max_upload_bytes": _MAX_UPLOAD_BYTES,
        "scenario_id": scenario_id,
    }


def parse_context_from_path(path):
    """
    Recover teacher_id/scenario_id from a file path shaped like
    'teachers/<teacher_id>/scenarios/<scenario_id>/<filename>'.

    Returns (teacher_id, scenario_id) as ints, or (None, None) if the
    path doesn't match the expected shape.
    """
    parts = path.strip("/").split("/")

    if len(parts) < 4 or parts[0] != "teachers" or parts[2] != "scenarios":
        return None, None

    try:
        return int(parts[1]), int(parts[3])
    except (ValueError, IndexError):
        return None, None


def resolve_file_url(path):
    """
    The file.uploaded webhook payload doesn't guarantee a resolved URL —
    fetch the file record to get one.
    """
    client = get_client()
    result = client.get_file(path)
    return result.file.url


def verify_webhook_signature(body, timestamp, signature, max_age_seconds=7200):
    """
    Verify that an incoming webhook notification genuinely came from
    Byteship. Byteship signs `{timestamp}.{body}` with HMAC-SHA256 and
    sends it as `v1=<hex digest>` in the Byteship-Webhook-Signature header.

    Each failure logs its reason, so a rejected webhook can be diagnosed
    from the server logs (the HTTP response is deliberately vague).
    """
    if _webhook_secret is None:
        logger.error("Byteship webhook rejected: webhook secret is not configured")
        return False

    try:
        ts = int(timestamp)
    except (TypeError, ValueError):
        logger.warning("Byteship webhook rejected: bad timestamp header %r", timestamp)
        return False

    if abs(time.time() - ts) > max_age_seconds:
        logger.warning("Byteship webhook rejected: timestamp outside %ss tolerance", max_age_seconds)
        return False

    expected = hmac.new(
        _webhook_secret.encode(),
        f"{timestamp}.{body}".encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(signature or "", f"v1={expected}"):
        logger.warning("Byteship webhook rejected: signature mismatch (wrong secret or altered body)")
        return False

    return True