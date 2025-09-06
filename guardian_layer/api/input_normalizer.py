# guardian_app/api/input_normalizer.py
from typing import Any, Dict, Optional, Tuple
from pydantic import BaseModel
import base64

TEXT_KEYS = {"text", "message", "msg", "content", "prompt"}
IMAGE_KEYS = {"image", "image_base64", "img", "data", "file", "photo"}
USER_KEYS = {"user", "user_id", "uid", "accountId"}

def _pluck_first(d: Dict[str, Any], keys: set) -> Optional[Any]:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None

def _dig(d: Any) -> Dict[str, Any]:
    # Flatten common wrappers like { data: {...} }, { payload: {...} }
    if not isinstance(d, dict):
        return {}
    for wrap in ("data", "payload", "body", "event", "request"):
        if wrap in d and isinstance(d[wrap], dict):
            # merge shallowly with preference for inner keys
            inner = d[wrap]
            merged = {**d, **inner}
            return merged
    return d

def guess_is_base64(s: str) -> bool:
    if not isinstance(s, str) or len(s) < 8:
        return False
    try:
        # quick sanity decode (ignore padding errors)
        base64.b64decode(s, validate=False)
        return True
    except Exception:
        return False

def normalize_payload_any(payload: Any) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Returns (text, image_base64, user_id) from an arbitrary payload.
    """
    if isinstance(payload, (str, bytes)):
        # plain body: treat as text if utf8-ish, else ignore
        try:
            s = payload.decode() if isinstance(payload, bytes) else payload
            return (s, None, None)
        except Exception:
            return (None, None, None)

    if not isinstance(payload, dict):
        return (None, None, None)

    flat = _dig(payload)

    # Try explicit type hints
    content_type = (flat.get("content_type") or flat.get("type") or flat.get("kind") or "").lower()

    # Pluck fields
    text = _pluck_first(flat, TEXT_KEYS)
    img = _pluck_first(flat, IMAGE_KEYS)
    user_id = _pluck_first(flat, USER_KEYS)

    # If content_type says "image" and only "content" provided, assume it's base64 image
    if not img and content_type.startswith("image") and isinstance(text, str) and guess_is_base64(text):
        img, text = text, None

    # If we still don't have img, check nested common shapes
    # e.g. { file: { buffer: "<b64>" } } or { image: { base64: "<b64>" } }
    if not img:
        for k in ("file", "image", "img", "photo"):
            v = flat.get(k)
            if isinstance(v, dict):
                img = v.get("base64") or v.get("data") or v.get("buffer") or v.get("content")
                if img:
                    break

    # If text looks like base64 and no image set, treat as image
    if isinstance(text, str) and not img and guess_is_base64(text):
        img, text = text, None

    # Coerce to strings
    text = str(text) if text is not None else None
    img = str(img) if img is not None else None
    user_id = str(user_id) if user_id is not None else None

    return (text, img, user_id)
