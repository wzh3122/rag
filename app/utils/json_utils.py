import json
import re
from typing import Any


def safe_json_loads(text: str, default: Any = None) -> Any:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            return default
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return default

