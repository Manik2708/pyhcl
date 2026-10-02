# pyhcl

A Python implementation of [HashiCorp HCL2](https://github.com/hashicorp/hcl),
ported from the Go reference implementation and checked against HashiCorp's
own conformance suite.

The goal is an API that feels like the standard `json` module:

```python
import pyhcl

data = pyhcl.loads(text)  # HCL text    -> Python data
text = pyhcl.dumps(data)  # Python data -> HCL text
```

## Status

**Early development. The parser is not implemented yet.** `loads` and `dumps`
are stubs, and the conformance suite does not pass. What exists today is the
scaffolding that tells us when it does:

| Piece | State |
| --- | --- |
| `pyhcl.loads` / `pyhcl.load` (reader) | stub, returns `{}` |
| `pyhcl.dumps` / `pyhcl.dump` (writer) | stub, returns `""` |
| `hcldec` adapter used by the conformance suite | written; does not yet apply `.hcldec` spec files |
| Conformance suite runner and CI | working |

This is a good moment to get involved: the work is cut into small, well-defined
pieces, and every piece has an official test waiting for it. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## How pyhcl tracks HCL

pyhcl is bound to exactly one release of `hashicorp/hcl`. The release tag lives
in [`src/pyhcl/HCL_VERSION`](src/pyhcl/HCL_VERSION) and is available at runtime:

```python
>>> import pyhcl
>>> pyhcl.__hcl_version__
'v2.24.0'
```

The conformance suite, CI and the published package all read that one file, so
a new upstream release never affects pyhcl until the tag is bumped on purpose.

## How pyhcl is tested

There are no unit tests for now. The single correctness gate is HashiCorp's
implementation-agnostic
[HCL spec suite](https://github.com/hashicorp/hcl/tree/main/specsuite), run by
their own Go runner (`hclspecsuite`) against pyhcl:

```
hclspecsuite (Go, from the pinned HCL release)
    └── runs each spec case through ──> hcldec (pyhcl.cli) ──> pyhcl.loads
```

The runner does not know or care that the implementation is written in Python.
It calls an executable named `hcldec`, and compares what comes back with the
expected result. pyhcl is conformant when every case passes.

## Development

You need [uv](https://docs.astral.sh/uv/), [Go](https://go.dev/dl/) and git.
uv installs the right Python version for you.

```sh
git clone git@github.com:Manik2708/pyhcl.git
cd pyhcl
uv sync                     # create .venv and install pyhcl + dev tools
scripts/run-specsuite.sh    # run the HCL conformance suite
```

The first run of the suite downloads the pinned HCL release into `.hcl/` and
builds the runner; later runs reuse both.

Code quality checks, the same ones CI runs:

```sh
uv run ruff format .        # format
uv run ruff check .         # lint
uv run mypy                 # type check
```

## Project layout

```
src/pyhcl/
  __init__.py     public API: load, loads, dump, dumps
  decode.py       reader: HCL text -> Python data   (port of Go's hclsyntax)
  encode.py       writer: Python data -> HCL text   (port of Go's hclwrite)
  cli.py          hcldec adapter that the conformance suite drives
  HCL_VERSION     the hashicorp/hcl release pyhcl is bound to
scripts/
  run-specsuite.sh    fetch the pinned HCL release and run its spec suite
.github/workflows/
  ci.yml          format, lint, type check and conformance suite
```
