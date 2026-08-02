---
name: awscost-release
description: Release awscost to PyPI. Bumps the version in pyproject.toml, commits it to master, and pushes a matching git tag (vX.Y.Z) that triggers the "release" GitHub Actions workflow (Trusted Publisher / OIDC, no token). The tag is always derived from pyproject.toml so the two never drift. Use for cutting a release, releasing, publishing to PyPI, bumping the version and tagging.
---

# awscost-release (cut a PyPI release)

Bump version → commit → push tag → GitHub Actions publishes to PyPI.

The whole flow is one script — [`release.sh`](release.sh). It is deterministic, so run it
rather than doing the steps by hand:

```bash
.claude/skills/awscost-release/release.sh [patch|minor|major|X.Y.Z]
```

- (none) or `patch` → bump the patch part (`0.4.0` → `0.4.1`)
- `minor` → `0.5.0`
- `major` → `1.0.0`
- an explicit `X.Y.Z` → set that exact version

**The git tag is always derived from `pyproject.toml`'s `version` as `v<version>`**, so the
tag and the packaged version never drift. `pyproject.toml` is the single source of truth.

## What the script does

1. Guards the working state: on `master`, clean tree, up to date with origin.
2. Reads the current version and computes the new one from the argument.
3. Stops on collision: tag already exists (local/origin) or version already on PyPI.
4. Edits the `version` line in `pyproject.toml`.
5. Sanity gate (mirrors `scripts/ci.sh run-test`): `ruff check src tests`,
   `ruff format --check --diff ./`, `pytest -q`; reverts `pyproject.toml` and stops on failure.
6. Commits `pyproject.toml` to `master` as `Release v<new>`, tags `v<new>` locally,
   then pushes `master`.
7. Pushes the tag — this is what triggers the `release` workflow.
8. Polls PyPI (~5 min) until `<new>` appears, then reports `https://pypi.org/project/awscost/<new>/`.

## Notes

- Releasing commits directly to `master` — the intentional exception to the "no direct work on
  master" rule. The script enforces the commit-before-tag order the publish workflow needs.
- Publishing is via PyPI Trusted Publisher (OIDC); no API token or `gh` is needed. It relies on
  the trusted publisher registered for `awscost` and the GitHub `pypi` Environment.
- `ruff` and `pytest` must be on PATH (`pip install ".[test]"` / `scripts/ci.sh install-test`).
- Confirm the new version with the user before running when the bump level is ambiguous.
- If publish fails with `File already exists`, that version is already on PyPI — bump again.
- Exit codes: `0` = published and confirmed; `2` = committed and tagged but PyPI not confirmed
  within the poll window (the publish is likely still running — check Actions, do **not** re-bump);
  `1` = a guard/gate failed before anything was pushed.
- If `master` is pushed but the tag push fails, the tag already exists locally — recover with
  `git push origin v<new>`; do not re-run the script (it would bump to the next version).
