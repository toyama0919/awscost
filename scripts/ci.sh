#!/bin/bash -e

install-test() {
  pip3 install ".[test]"
}

run-test() {
  ruff check src tests
  ruff format --check --diff ./
  pytest -v --capture=no
}

release() {
  # push a git tag; the release workflow uploads to PyPI on tag push
  VERSION=$(grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
  git tag v${VERSION}
  git push origin --tags
}

$@
