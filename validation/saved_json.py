"""Writing and reading saved validation results.

The test classes return numpy bools (np.True_ / np.False_). json can't
serialise those, and the old `default=str` wrote them as the strings
"True" / "False". `json_default` writes them as real JSON booleans instead,
and `is_pass` reads a verdict correctly from either kind of file.
"""
import numpy as np


def json_default(obj):
    """`default=` hook for json.dump: numpy bools become real booleans."""
    if isinstance(obj, np.bool_):
        return bool(obj)
    return str(obj)


def is_pass(value) -> bool:
    """True only for a passing verdict, including "True" strings from older files."""
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)
