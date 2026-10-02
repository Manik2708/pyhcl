"""pyhcl — a Python implementation of HashiCorp HCL2 (reader + writer).

Ported from github.com/hashicorp/hcl/v2, exposed with a json-module-style API:

    import pyhcl
    data = pyhcl.loads(text)     # HCL text  -> Python data
    text = pyhcl.dumps(data)     # Python data -> HCL text

Conformance will be validated against HCL's own implementation-agnostic spec
suite once the reader/writer are implemented.
"""

from __future__ import annotations

from importlib.resources import files

from .decode import load, loads
from .encode import dump, dumps

__version__ = "0.0.1"

# The hashicorp/hcl release this version of pyhcl is ported from and tested
# against. HCL_VERSION is the single source of truth: the spec-suite runner
# (scripts/run-specsuite.sh) and CI read the same file.
__hcl_version__ = files(__name__).joinpath("HCL_VERSION").read_text().strip()

__all__ = ["load", "loads", "dump", "dumps", "__version__", "__hcl_version__"]
