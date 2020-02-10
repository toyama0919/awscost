from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
print(open(os.path.join(here, "README.md")).read())
version = "0.2.0"

install_requires = ["tabulate", "boto3", "click>=7.0"]

setup(
    name="awscost",
    scripts=["bin/awscost"],
    version=version,
    description="Command Line utility for cost of aws.",
    long_description=open(os.path.join(here, "README.md")).read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="awscost tool aws",
    author="Hiroshi Toyama",
    author_email="toyama0919@gmail.com",
    url="https://github.com/toyama0919/awscost",
    license="MIT",
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    entry_points={"console_scripts": ["awscost=awscost.commands:main"]},
)
