# api/cloudinary.py
#
# Cloudinary adapter for video upload and webhook handling.
# SDK is initialized via init_cloudinary(app) in extensions.py.

import time

import cloudinary
import cloudinary.utils


def generate_upload_url(scenario_id, teacher_id):
    """
    Build signed upload parameters for direct client-side upload to Cloudinary.

    The client POSTs these params (plus the video file) directly to:
        https://api.cloudinary.com/v1_1/<cloud_name>/video/upload

    Cloudinary never touches your server during the upload itself.
    The webhook (handle_cloudinary_webhook) handles completion notification.

    Returns:
    {
        "upload_url": "https://api.cloudinary.com/v1_1/<cloud_name>/video/upload",
        "fields": {
            "api_key": ...,
            "timestamp": ...,
            "folder": ...,
            "context": ...,
            "signature": ...
        },
        "scenario_id": scenario_id
    }
    """
    cfg = cloudinary.config()

    timestamp = int(time.time())

    folder = f"verifyteach/teachers/{teacher_id}"

    # Context is stored as key=value pairs on the Cloudinary asset.
    # Cloudinary echoes these back in the webhook payload.
    context = f"teacher_id={teacher_id}|scenario_id={scenario_id}"

    params_to_sign = {
        "timestamp": timestamp,
        "folder": folder,
        "context": context,
    }

    signature = cloudinary.utils.api_sign_request(
        params_to_sign,
        cfg.api_secret,
    )

    upload_url = (
        f"https://api.cloudinary.com/v1_1/{cfg.cloud_name}/video/upload"
    )

    return {
        "upload_url": upload_url,
        "fields": {
            "api_key": cfg.api_key,
            "timestamp": timestamp,
            "folder": folder,
            "context": context,
            "signature": signature,
        },
        "scenario_id": scenario_id,
    }


def verify_webhook_signature(body, timestamp, signature):
    """
    Verify that an incoming webhook notification genuinely came from Cloudinary.

    Args:
        body:      Raw request body string (JSON).
        timestamp: Value of the X-Cld-Timestamp header.
        signature: Value of the X-Cld-Signature header.

    Returns:
        True if the signature is valid and the request is recent, False otherwise.
    """
    try:
        return cloudinary.utils.verify_notification_signature(
            body,
            timestamp,
            signature,
            valid_for=7200,  # reject notifications older than 2 hours
        )
    except Exception:
        return False
