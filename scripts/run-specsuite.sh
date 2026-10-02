#!/usr/bin/env bash
#
# run-specsuite.sh — run HashiCorp's official HCL conformance suite against our
# Python hcldec implementation.
#
# pyhcl is bound to exactly one hashicorp/hcl release, named in
# src/pyhcl/HCL_VERSION (also exposed as pyhcl.__hcl_version__). This script
# fetches that release, builds its spec-suite runner (cmd/hclspecsuite), and
# invokes it against our hcldec adapter. The runner walks every case in
# hcl/specsuite/tests, asks our implementation to decode it, and diffs the
# result against the expected .t file.
#
# To upgrade to a newer HCL release, change the tag in src/pyhcl/HCL_VERSION
# and make the suite pass again. Nothing else tracks upstream.
#
# Usage:
#   scripts/run-specsuite.sh
#
# Environment:
#   HCLDEC    path to the hcldec executable to test (default: .venv/bin/hcldec,
#             the entry point 'uv sync' installs for pyhcl.cli)
#   HCL_DIR   use this hashicorp/hcl checkout instead of the pinned release.
#             For local experiments only (e.g. trying an unreleased upstream
#             commit); CI always runs the pinned release.
#
set -euo pipefail

# --- resolve paths ----------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"                      # the pyhcl/ project root
CACHE="$ROOT/.hcl"                                        # git-ignored

HCLDEC="${HCLDEC:-$ROOT/.venv/bin/hcldec}"
if [[ ! -x "${HCLDEC}" ]]; then
  echo "error: hcldec executable not found or not executable: ${HCLDEC}" >&2
  echo "       (run 'uv sync' in ${ROOT} to install it)" >&2
  exit 2
fi

# --- locate the HCL sources --------------------------------------------------
if [[ -n "${HCL_DIR:-}" ]]; then
  echo ">> WARNING: HCL_DIR is set; using ${HCL_DIR} instead of the pinned release" >&2
  RUNNER="$CACHE/bin/hclspecsuite-custom"
  rm -f "${RUNNER}"                       # a custom checkout can change; always rebuild
else
  HCL_VERSION="$(tr -d '[:space:]' < "$ROOT/src/pyhcl/HCL_VERSION")"
  if [[ ! "${HCL_VERSION}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "error: src/pyhcl/HCL_VERSION must be a hashicorp/hcl release tag like v2.24.0" >&2
    echo "       (got: '${HCL_VERSION}')" >&2
    exit 2
  fi

  HCL_DIR="$CACHE/src/${HCL_VERSION}"
  RUNNER="$CACHE/bin/hclspecsuite-${HCL_VERSION}"
  if [[ ! -d "${HCL_DIR}/specsuite/tests" ]]; then
    echo ">> fetching hashicorp/hcl ${HCL_VERSION}" >&2
    rm -rf "${HCL_DIR}"
    git -c advice.detachedHead=false clone --quiet --depth 1 \
      --branch "${HCL_VERSION}" https://github.com/hashicorp/hcl.git "${HCL_DIR}"
  fi
fi

if [[ ! -d "${HCL_DIR}/specsuite/tests" ]]; then
  echo "error: no specsuite/tests dir under: ${HCL_DIR}" >&2
  exit 2
fi

# --- build the official runner from those sources ---------------------------
# Building inside the checkout uses its go.mod, so the runner is the exact
# version that ships with the spec cases. A release tag never changes, so the
# pinned runner is built once and reused.
if [[ ! -x "${RUNNER}" ]]; then
  echo ">> building hclspecsuite from ${HCL_DIR}" >&2
  mkdir -p "$(dirname "${RUNNER}")"
  ( cd "${HCL_DIR}" && go build -o "${RUNNER}" ./cmd/hclspecsuite )
fi

# --- run the suite against our implementation -------------------------------
echo ">> running specsuite: ${RUNNER} ${HCL_DIR}/specsuite/tests ${HCLDEC}" >&2
echo >&2
exec "${RUNNER}" "${HCL_DIR}/specsuite/tests" "${HCLDEC}"
