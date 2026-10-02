"""Encoding: Python values -> HCL text.

Mirrors the write side of github.com/hashicorp/hcl/v2 (hclwrite + gohcl
encode), exposed with a json-module-style API.

SKELETON: the functions below define the input/output structure of the writer.
The actual serializer is not implemented yet, so `dumps` currently returns an
empty document.
"""

from __future__ import annotations

from typing import IO, Any


def dumps(value: Any, *, indent: int = 2) -> str:
    """Serialize Python data to a formatted HCL document string.

    `value` is a dict of attribute names -> values and block types -> contents,
    the same shape produced by decode.loads, analogous to json.dumps.

    TODO: implement the HCL writer/formatter.
    """
    _ = (value, indent)  # unused until implemented
    return ""


def dump(value: Any, fp: IO[str], *, indent: int = 2) -> None:
    """Serialize Python data as HCL to a text file-like object (see `dumps`)."""
    fp.write(dumps(value, indent=indent))
