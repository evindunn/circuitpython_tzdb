# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Evin Dunn
#
# SPDX-License-Identifier: MIT

"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    requirements = [l.strip() for l in f.readlines()]

setup(
    # Community Bundle Information
    name="circuitpython-tzdb",
    use_scm_version={
        # This is needed for the PyPI version munging in the Github Actions release.yml
        "git_describe_command": "git describe --tags --long",
        "local_scheme": "no-local-version",
    },
    setup_requires=["setuptools_scm"],
    description="IANA timezones for adafruit_datetime",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # The project's main homepage.
    url="https://github.com/evindunn/CircuitPython_tzdb.git",
    # Author details
    author="Evin Dunn",
    author_email="evindunn14@gmail.com",
    install_requires=requirements,
    # Choose your license
    license="MIT",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Hardware",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    # What does your project relate to?
    keywords="adafruit blinka circuitpython micropython tzdb datetime timezone",
    packages=["tzdb"],
)
