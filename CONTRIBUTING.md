# Contributing to pyhcl

Thanks for helping out. This project welcomes first-time open-source
contributors, and this guide assumes no prior experience with the codebase.
If a step here is unclear or does not work, that is a bug in the guide: please
open an issue.

## What we are building

pyhcl is a Python port of HashiCorp's Go implementation of HCL2. We are not
designing a language. The behaviour is already defined by the Go code and by
[the HCL spec](https://github.com/hashicorp/hcl/blob/main/hclsyntax/spec.md).
Our job is to reproduce it in Python.

Success is measured by one thing: HashiCorp's official conformance suite
passing against pyhcl. Read the [README](README.md) first for the overall
picture.

## Setting up

You need:

- [uv](https://docs.astral.sh/uv/getting-started/installation/), which manages
  Python and the dependencies
- [Go](https://go.dev/dl/), only to build HashiCorp's test runner
- git

Then:

1. Fork the repository on GitHub and clone your fork.

   ```sh
   git clone git@github.com:<your-username>/pyhcl.git
   cd pyhcl
   ```

2. Install everything.

   ```sh
   uv sync
   ```

3. Run the conformance suite to check your setup.

   ```sh
   scripts/run-specsuite.sh
   ```

   The first run downloads the pinned HCL release into `.hcl/` and builds the
   runner, so it takes a little longer. **Seeing failures here is expected**:
   most of the parser is not written yet. The setup is working if the suite
   runs and prints results for each case.

## How the conformance suite works

Each test case is a set of files with the same name. For example
`structure/attributes/expected`:

| File | What it is |
| --- | --- |
| `expected.hcl` | the HCL input |
| `expected.hcldec` | a spec describing which attributes and blocks to decode |
| `expected.t` | the expected result, and any errors that must be reported |

After the first run you can read every case under
`.hcl/src/<version>/specsuite/tests/`.

HashiCorp's runner feeds each case to our `hcldec` command
(`src/pyhcl/cli.py`), which calls `pyhcl.loads` and prints the result. The
runner compares that with the `.t` file and reports one of:

- **Incorrect result value** or **Incorrect result type**: we decoded the input
  to the wrong thing.
- **Missing expected diagnostic**: the input is invalid and we were supposed to
  report an error at a specific position, but did not.

A case with no errors printed under its name has passed.

## Making a change

1. **Pick an issue.** Issues labelled `good first issue` are a good place to
   start. Comment on the issue before you begin, so that two people do not do
   the same work.

2. **Create a branch.**

   ```sh
   git switch -c fix-hash-comments
   ```

3. **Read the Go code you are porting.** The reference implementation is
   already on your machine after the first suite run, under
   `.hcl/src/<version>/`:

   | You are working on | Read this Go package |
   | --- | --- |
   | `src/pyhcl/decode.py` (reader) | `hclsyntax/` |
   | `src/pyhcl/encode.py` (writer) | `hclwrite/` |
   | `src/pyhcl/cli.py` (spec handling) | `cmd/hcldec/`, `hcldec/` |

   Port the behaviour, not the syntax. Write Python that a Python developer
   would recognise, with type hints.

4. **Run the suite** and check that your target case now passes and that no
   case that passed before has started failing.

   ```sh
   scripts/run-specsuite.sh
   ```

5. **Run the code checks.** CI runs the same three and fails the pull request
   if any of them do.

   ```sh
   uv run ruff format .
   uv run ruff check .
   uv run mypy
   ```

   `ruff check --fix .` fixes many lint problems for you.

6. **Open a pull request** against `master`. In the description, say which
   spec case or issue it addresses and which cases pass now that did not
   before.

## Ground rules

- **The spec suite is the only test.** Please do not add unit tests or pytest
  for now. If you think a behaviour is not covered by the suite, open an issue
  to discuss it.
- **HCL in files, not in strings.** Any HCL used for testing belongs in its own
  `.hcl` file, never inline as a Python string.
- **No runtime dependencies.** The library itself uses only the standard
  library. Development tools go in the `dev` dependency group.
- **Do not change `src/pyhcl/HCL_VERSION` in a feature pull request.** It binds
  the whole project to one upstream HCL release. Upgrades are done separately
  and on purpose.
- **Keep pull requests small.** One spec case or one fix per pull request is
  easier to review and quicker to merge.
- **Type everything.** mypy runs in strict mode, so every function needs type
  annotations.

## CI

Every pull request runs two jobs:

- **checks**: `ruff format --check`, `ruff check` and `mypy`. This must be
  green.
- **specsuite**: the full conformance suite. It stays red until every case
  passes, so a red result on your pull request does not by itself mean you
  broke something. Compare the failing cases with those on `master`.

## Getting help

Stuck on setup, on reading the Go code, or on what a spec case expects? Ask in
the issue you are working on, or open a new one. Questions are welcome.
