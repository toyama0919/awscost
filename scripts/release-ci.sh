#!/bin/bash -eu

# build dist
python setup.py sdist bdist_wheel

# git tag
git tag v$(python setup.py --version)
git push origin --tags

# pypi upload
twine upload --verbose dist/awscost-$(python setup.py --version).tar.gz
