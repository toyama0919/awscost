#!/bin/bash -eu
tox -e release

# git tag
git tag v$(python setup.py --version)
git push origin --tags
