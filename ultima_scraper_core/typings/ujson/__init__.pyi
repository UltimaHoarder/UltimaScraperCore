"""
Type stubs for ujson (ultra-fast JSON library).

ujson is a C-based JSON encoder/decoder that's faster than the standard library.
These type stubs provide proper type hints for better IDE support and type checking.
"""

from typing import Any, IO, overload

# loads() - Deserialize JSON string to Python object
@overload
def loads(
    s: str | bytes,
) -> Any: ...

@overload
def loads(
    s: str | bytes,
    precise_float: bool = ...,
) -> Any: ...

def loads(
    s: str | bytes,
    precise_float: bool = False,
) -> Any:
    """
    Deserialize JSON string to Python object.
    
    Args:
        s: JSON string or bytes to parse
        precise_float: Use higher precision for floats (slower)
    
    Returns:
        Parsed Python object (dict, list, str, int, float, bool, None)
    """
    ...

# dumps() - Serialize Python object to JSON string
def dumps(
    obj: Any,
    ensure_ascii: bool = True,
    double_precision: int = 9,
    encode_html_chars: bool = False,
    escape_forward_slashes: bool = True,
    sort_keys: bool = False,
    indent: int = 0,
) -> str:
    """
    Serialize Python object to JSON string.
    
    Args:
        obj: Python object to serialize
        ensure_ascii: Escape non-ASCII characters
        double_precision: Number of decimal places for floats
        encode_html_chars: Encode HTML characters (<, >, &)
        escape_forward_slashes: Escape forward slashes in strings
        sort_keys: Sort dictionary keys alphabetically
        indent: Number of spaces for pretty-printing (0 = compact)
    
    Returns:
        JSON string
    """
    ...

# dump() - Serialize Python object to JSON file
def dump(
    obj: Any,
    fp: IO[str],
    ensure_ascii: bool = True,
    double_precision: int = 9,
    encode_html_chars: bool = False,
    escape_forward_slashes: bool = True,
    sort_keys: bool = False,
    indent: int = 0,
) -> None:
    """
    Serialize Python object to JSON file.
    
    Args:
        obj: Python object to serialize
        fp: File-like object to write to
        ensure_ascii: Escape non-ASCII characters
        double_precision: Number of decimal places for floats
        encode_html_chars: Encode HTML characters (<, >, &)
        escape_forward_slashes: Escape forward slashes in strings
        sort_keys: Sort dictionary keys alphabetically
        indent: Number of spaces for pretty-printing (0 = compact)
    """
    ...

# load() - Deserialize JSON file to Python object
def load(
    fp: IO[str],
    precise_float: bool = False,
) -> Any:
    """
    Deserialize JSON file to Python object.
    
    Args:
        fp: File-like object to read from
        precise_float: Use higher precision for floats (slower)
    
    Returns:
        Parsed Python object (dict, list, str, int, float, bool, None)
    """
    ...

# encode() - Alias for dumps()
def encode(
    obj: Any,
    ensure_ascii: bool = True,
    double_precision: int = 9,
    encode_html_chars: bool = False,
    escape_forward_slashes: bool = True,
    sort_keys: bool = False,
    indent: int = 0,
) -> str:
    """Alias for dumps()."""
    ...

# decode() - Alias for loads()
def decode(
    s: str | bytes,
    precise_float: bool = False,
) -> Any:
    """Alias for loads()."""
    ...
