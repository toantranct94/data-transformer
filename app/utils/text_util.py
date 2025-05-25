import json
import re
from distutils.util import strtobool


def try_parse_string(answer: str, default: dict):
    try:
        answer = answer.replace("```json", "")
        answer = answer.replace("```", "")
        return json.loads(answer)
    except json.JSONDecodeError:
        return default


def try_parse_float(value: str, default=0):
    try:
        value = str(value)
        match = re.search(r"\d+", value)
        if match:
            return float(match.group())
        else:
            return default
    except (ValueError, TypeError):
        return default


def try_parse_bool(value: str | bool, default=False):
    if isinstance(value, bool):
        return value
    try:
        return bool(strtobool(value))
    except (ValueError, TypeError):
        return default
