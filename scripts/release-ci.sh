#!/bin/bash -eu

python setup.py sdist bdist_wheel
twine upload --verbose dist/awscost-$(python setup.py --version).tar.gz
