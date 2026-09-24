# api/gemini.py
#
# Google Gemini adapter — drop-in replacement for api/cencori.py's
# generate_scenario() and review_video(), using the same function
# signatures and return shapes so services/scenario_service.py and
# services/review_service.py don't need to change their calling code.
#
# Why Gemini instead of Cencori: the AIB Ship $50 Cencori credit hadn't
# been applied to our account as of build time (support ticket open).
# Gemini's free tier (no card required) unblocks us without waiting.
# Swapping back later is a one-line import change in scenario_service.py
# and review_service.py, since the contract is identical.
#
# Setup: pip install google-genai requests
# Env var required: GEMINI_API_KEY (free, no card: https://aistudio.google.com/apikey)

import os
import json
import tempfile
import time

import requests
from google import genai
from google.genai import types
from google.genai.errors import APIError

from errors.exceptions import AIServiceError

_API_KEY = os.environ.get("GEMINI_API_KEY")
_client = genai.Client(
    api_key=_API_KEY,
    http_options=types.HttpOptions(timeout=15000),  # 15s, in ms
) if _API_KEY else None
_MODEL = "gemini-3.6-flash"

def _require_client():
    if _client is None:
        raise AIServiceError(
            "GEMINI_API_KEY is not configured on the server. "
            "Set it in your environment (Render dashboard + local .env)."
        )


# ---------------------------------------------------------------------
# generate_scenario — matches api/cencori.py's contract exactly:
# input (subject, level) -> {"prompt_text": "..."}
# ---------------------------------------------------------------------

def generate_scenario(subject, level):
    _require_client()

    prompt = f"""You are creating a short teaching scenario for a teacher applicant to
demonstrate their teaching ability on video, as part of a job-screening process.

Generate ONE realistic classroom teaching scenario for:
- Subject: {subject}
- Grade/level: {level}

Requirements:
- Describe a specific situation the teacher must teach or explain, aimed at pupils of the stated level.
- It must be answerable in a 2-3 minute recorded video.
- Do not include an answer key or explanation - only the scenario/prompt itself.
- Keep it realistic to a Nigerian classroom context.
- Output ONLY the scenario text. No preamble, no headers, no markdown.

Now generate the scenario."""

    try:
        response = _client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
               temperature=0.9,
               max_output_tokens=1024,
               thinking_config=types.ThinkingConfig(thinking_level="LOW"),
            ),
        )
    except APIError as e:
        raise AIServiceError(f"Gemini API error while generating scenario: {str(e)}")
    except Exception as e:
        raise AIServiceError(f"Unexpected error generating scenario: {str(e)}")

    prompt_text = (response.text or "").strip()
    if not prompt_text:
        raise AIServiceError("Gemini returned an empty scenario.")

    return {"prompt_text": prompt_text}


# ---------------------------------------------------------------------
# review_video — matches api/cencori.py's contract exactly:
# input (prompt_text, video_url) -> {"score", "notes", "flagged", "flag_reason"}
# ---------------------------------------------------------------------

_REVIEW_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "notes": {"type": "string"},
        "flagged": {"type": "boolean"},
        "flag_reason": {"type": "string"},
    },
    "required": ["score", "notes", "flagged"],
}

_REVIEW_INSTRUCTIONS = """You are an experienced education reviewer assessing a teacher applicant's
recorded teaching demonstration video, submitted in response to a specific scenario prompt.

The scenario the teacher was asked to teach was:
"{prompt_text}"

Watch the video and assess:
- Subject knowledge accuracy
- Clarity of explanation for the stated audience
- Classroom presence and communication
- Any concerning behavior toward children (bias, inappropriate conduct, harmful
  teaching methods) - this matters more than polish, since children's safety
  and wellbeing come first.

Return a score from 0-100, brief notes explaining the score, whether this video
should be FLAGGED for mandatory human reviewer attention (true if there is ANY
concern about pedagogy quality, bias, or child safety - err on the side of
flagging when uncertain), and if flagged, a short flag_reason."""


def review_video(prompt_text, video_url):
    _require_client()

    tmp_path = _download_video(video_url)
    uploaded_file = None

    try:
        uploaded_file = _client.files.upload(file=tmp_path)
        uploaded_file = _wait_for_file_active(uploaded_file)

        try:
            response = _client.models.generate_content(
                model=_MODEL,
                contents=[
                    uploaded_file,
                    _REVIEW_INSTRUCTIONS.format(prompt_text=prompt_text),
                ],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                    response_json_schema=_REVIEW_JSON_SCHEMA,
                    thinking_config=types.ThinkingConfig(thinking_level="LOW"),
                ),
            )
        except APIError as e:
            raise AIServiceError(f"Gemini API error while reviewing video: {str(e)}")

        try:
            result = json.loads(response.text)
        except (json.JSONDecodeError, TypeError) as e:
            raise AIServiceError(f"Gemini returned an unparseable review response: {str(e)}")

        result.setdefault("flag_reason", None)
        return result

    finally:
        # Clean up: local temp file always; remote Gemini file best-effort
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        if uploaded_file is not None:
            try:
                _client.files.delete(name=uploaded_file.name)
            except Exception:
                pass  # not worth failing the request over cleanup


def _download_video(video_url, max_bytes=200 * 1024 * 1024):
    """Downloads the video from Cloudinary (or wherever it's hosted) to a
    local temp file, since Gemini's Files API needs a local file/stream,
    not a bare URL."""
    try:
        resp = requests.get(video_url, stream=True, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise AIServiceError(f"Could not download video for review: {str(e)}")

    suffix = os.path.splitext(video_url.split("?")[0])[1] or ".mp4"
    fd, tmp_path = tempfile.mkstemp(suffix=suffix)

    total = 0
    with os.fdopen(fd, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            total += len(chunk)
            if total > max_bytes:
                f.close()
                os.remove(tmp_path)
                raise AIServiceError("Video exceeds the maximum size accepted for AI review.")
            f.write(chunk)

    return tmp_path


def _wait_for_file_active(file_obj, timeout_seconds=120, poll_interval=3):
    """Gemini processes uploaded video asynchronously. Poll until it's
    ACTIVE (usable) or FAILED, rather than assuming it's ready immediately."""
    waited = 0
    while file_obj.state == "PROCESSING":
        if waited >= timeout_seconds:
            raise AIServiceError("Timed out waiting for Gemini to process the video.")
        time.sleep(poll_interval)
        waited += poll_interval
        file_obj = _client.files.get(name=file_obj.name)

    if file_obj.state == "FAILED":
        raise AIServiceError("Gemini failed to process the uploaded video.")

    return file_obj


