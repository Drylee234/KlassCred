# api/cloudinary.py
#
# Cloudinary adapter for video upload and webhook handling.
# SDK is already initialized in extensions.py via init_cloudinary(app).
#
# All functions in this module are stubs.
# Replace each `pass` block with the real Cloudinary SDK call
# once the integration is ready.


def generate_upload_url(scenario_id, teacher_id):
    """
    Generate a signed Cloudinary upload URL for direct client upload.

    Expected return:
    {
        "upload_url": "...",
        "scenario_id": scenario_id
    }
    """
    pass


def verify_webhook_signature(payload, signature):
    """
    Verify that an incoming webhook request genuinely came from Cloudinary.

    Expected return:
        True/False
    """
    pass