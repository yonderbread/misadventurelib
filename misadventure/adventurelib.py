import re
import sys
import inspect

try:
    import readline  # noqa: adds readline semantics to input()
except ImportError:
    pass
import textwrap

try:
    from shutil import get_terminal_size
except ImportError:
    try:
        from backports.shutil_get_terminal_size import get_terminal_size
    except ImportError:
        def get_terminal_size(fallback=(80, 24)):
            return fallback


