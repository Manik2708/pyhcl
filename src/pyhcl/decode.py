"""Decoding: HCL text -> Python values.

Mirrors the read side of github.com/hashicorp/hcl/v2 (hclsyntax parser +
gohcl/hcldec decoding), exposed with a json-module-style API.

SKELETON: the functions below define the input/output structure of the reader.
The actual scanner/parser is not implemented yet, so `loads` currently returns
an empty document.
"""

from __future__ import annotations

from typing import IO, Any


def loads(src: str, *, filename: str = "<string>") -> dict[str, Any]:
    """Parse an HCL document from a string into Python data.

    The result is a dict mapping top-level attribute names to their values and
    block types to their decoded contents, analogous to json.loads.

    TODO: implement the HCL2 scanner + parser.
    """
    _ = (src, filename)  # unused until implemented
    return {}


def load(fp: IO[str], *, filename: str | None = None) -> dict[str, Any]:
    """Parse an HCL document from a text file-like object (see `loads`)."""
    name = filename or str(getattr(fp, "name", "<file>"))
    return loads(fp.read(), filename=name)
