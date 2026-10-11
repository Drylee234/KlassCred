# api/cloudinary.py
"""Cloudinary signing helpers for direct browser video uploads."""

import time

import cloudinary
import cloudinary.utils


def generate_upload_url(scenario_id, teacher_id):
    """Return a short-lived signed upload request; the API secret stays server-side."""
    cfg = cloudinary.config()
    if not cfg.cloud_name or not cfg.api_key or not cfg.api_secret:
        raise RuntimeError("Cloudinary is not configured")

    timestamp = int(time.time())
    folder = f"klasscred/teachers/{teacher_id}/scenarios/{scenario_id}"
    context = f"teacher_id={teacher_id}|scenario_id={scenario_id}"
    params = {
        "timestamp": timestamp,
        "folder": folder,
        "context": context,
        "resource_type": "video",
    }
    signature = cloudinary.utils.api_sign_request(
        {key: value for key, value in params.items() if key != "resource_type"},
        cfg.api_secret,
    )

    return {
        "upload_url": f"https://api.cloudinary.com/v1_1/{cfg.cloud_name}/video/upload",
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
    """Verify Cloudinary's timestamped notification signature."""
    try:
        return cloudinary.utils.verify_notification_signature(
            body,
            timestamp,
            signature,
            valid_for=7200,
        )
    except Exception:
        return False
