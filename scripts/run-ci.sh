#!/bin/bash -eu

tox -e black-check
tox -e flake8
tox -e pytest
