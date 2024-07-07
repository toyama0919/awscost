#!/bin/bash -e

install-test() {
  pip3 install ".[test]"
}

run-test() {
  tox -e black-check
  tox -e flake8
  tox -e pytest
}

release() {
  # upload pypi
  tox -e release
  # git tag
  VERSION=$(grep -m 1 version pyproject.toml | tr -s ' ' | tr -d '"' | tr -d "'" | cut -d' ' -f3)
  git tag v${VERSION}
  git push origin --tags
}

$@
