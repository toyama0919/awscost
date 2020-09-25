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
  git tag v$(python setup.py --version)
  git push origin --tags
}

$@
