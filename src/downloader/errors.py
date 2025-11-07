import os
import json
import random
from django.conf import settings

_DEFAULT_FALLBACK_ERROR = "❌ Oh no, something went wrong..."

def _load_error_messages():
    try:
        base = settings.BASE_DIR
        file_path = os.path.abspath(os.path.join(base, 'static', 'messages', 'error_messages.json'))
    except Exception:
        return [_DEFAULT_FALLBACK_ERROR]

    try:
        if not os.path.exists(file_path):
            return [_DEFAULT_FALLBACK_ERROR]

        with open(file_path, 'r', encoding='utf-8') as fh:
            data = json.load(fh)

        if isinstance(data, list) and data:
            msgs = [str(s).strip() for s in data if isinstance(s, str) and s.strip()]
            if msgs:
                return msgs

    except Exception:
        return [_DEFAULT_FALLBACK_ERROR]

    return [_DEFAULT_FALLBACK_ERROR]


FRIENDLY_ERRORS_MSGS = _load_error_messages()

def pick_friendly_error():
    try:
        return random.choice(FRIENDLY_ERRORS_MSGS)
    except Exception:
        return _DEFAULT_FALLBACK_ERROR
