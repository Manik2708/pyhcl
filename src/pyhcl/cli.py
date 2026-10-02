"""hcldec — a CLI adapter that lets HashiCorp's HCL spec suite drive pyhcl.

HashiCorp's `hclspecsuite` runner tests any HCL implementation by shelling out
to an external `hcldec` executable. This module provides that executable using
Typer (a Cobra-style CLI framework), bridging the protocol to our library.

It contains NO HCL logic of its own — it imports `pyhcl` and calls it. The CLI
owns only the protocol concerns: flags, reading spec/input files, encoding the
result as cty-JSON, and emitting JSON diagnostics.

Protocol (as invoked by cmd/hclspecsuite):

    hcldec --spec=<spec> --diags=json --with-type --keep-nulls <input>
      stdout : decoded result as cty-JSON, wrapped {"value":.., "type":..}
      stderr : {"diagnostics": [...]}   (JSON)
      exit   : 0 ok, non-zero on error diagnostics
"""

from __future__ import annotations

import json
import sys
from typing import Any

import typer

import pyhcl

app = typer.Typer(add_completion=False, help="Decode an HCL file per an hcldec spec.")


# --- cty-JSON encoding ------------------------------------------------------
# cty expects a {"value": V, "type": T} pair. An HCL `[..]` literal is a cty
# tuple and `{..}` is a cty object, so we type them structurally.


def to_cty(value: Any) -> tuple[Any, Any]:
    """Return (json_value, cty_type_json) for a Python value."""
    if value is None:
        return None, "dynamic"
    if isinstance(value, bool):
        return value, "bool"
    if isinstance(value, (int, float)):
        return value, "number"
    if isinstance(value, str):
        return value, "string"
    if isinstance(value, (list, tuple)):
        vals: list[Any] = []
        types: list[Any] = []
        for elem in value:
            v, t = to_cty(elem)
            vals.append(v)
            types.append(t)
        return vals, ["tuple", types]
    if isinstance(value, dict):
        attrs: dict[str, Any] = {}
        attr_types: dict[str, Any] = {}
        for key, elem in value.items():
            v, t = to_cty(elem)
            attrs[str(key)] = v
            attr_types[str(key)] = t
        return attrs, ["object", attr_types]
    raise TypeError(f"cannot encode {type(value).__name__} as cty value")


# --- diagnostics ------------------------------------------------------------


def _diag(summary: str, detail: str = "") -> dict[str, str]:
    d = {"severity": "error", "summary": summary}
    if detail:
        d["detail"] = detail
    return d


def _emit_diags(diags: list[dict[str, str]], fmt: str | None) -> None:
    if not diags:
        return
    if fmt == "json":
        sys.stderr.write(json.dumps({"diagnostics": diags}))
    else:
        for d in diags:
            sys.stderr.write(f"{d['severity']}: {d['summary']}\n")
    sys.stderr.flush()


# --- command ----------------------------------------------------------------

VERSION = "0.0.1-dev"


@app.command()
def hcldec(
    input_file: str | None = typer.Argument(
        None, metavar="INPUT", help="input HCL file"
    ),
    spec: str | None = typer.Option(
        None, "--spec", "-s", help="path to hcldec spec file"
    ),
    out: str | None = typer.Option(
        None, "--out", "-o", help="write result here instead of stdout"
    ),
    diags: str | None = typer.Option(
        None, "--diags", help='diagnostics format ("json")'
    ),
    with_type: bool = typer.Option(
        False, "--with-type", help="wrap result with its cty type"
    ),
    keep_nulls: bool = typer.Option(
        False, "--keep-nulls", help="retain null object attributes"
    ),
    var_refs: bool = typer.Option(
        False, "--var-refs", help="describe referenced variables instead of decoding"
    ),
    version: bool = typer.Option(False, "--version", help="print version and exit"),
) -> None:
    if version:
        typer.echo(VERSION)
        raise typer.Exit(0)

    problems: list[dict[str, str]] = []
    if not spec:
        problems.append(_diag("the --spec=... argument is required"))
    if not input_file:
        problems.append(_diag("an input file is required"))
    if problems or not input_file:
        _emit_diags(problems, diags)
        raise typer.Exit(1)

    try:
        with open(input_file) as f:
            input_src = f.read()
    except OSError as err:
        _emit_diags([_diag("Failed to read input file", str(err))], diags)
        raise typer.Exit(1) from None

    # --- the one place we call the library ---
    # NOTE: the .hcldec spec is not yet applied; the whole decoded body is
    # passed through. Object-shaped specs will match once pyhcl.loads works;
    # block/collection specs need spec interpretation, added later.
    try:
        data = pyhcl.loads(input_src, filename=input_file)
    except Exception as err:  # surface library errors as diagnostics
        _emit_diags([_diag("Failed to decode input", str(err))], diags)
        raise typer.Exit(1) from None

    if var_refs:
        sys.stdout.write(json.dumps([]))  # traversal support: TODO
        sys.stdout.flush()
        raise typer.Exit(0)

    try:
        value, cty_type = to_cty(data)
    except TypeError as err:
        _emit_diags([_diag("Failed to encode result", str(err))], diags)
        raise typer.Exit(1) from None

    result = (
        json.dumps({"value": value, "type": cty_type})
        if with_type
        else json.dumps(value)
    )
    if out:
        with open(out, "w") as f:
            f.write(result)
    else:
        sys.stdout.write(result)
        sys.stdout.flush()
    raise typer.Exit(0)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
