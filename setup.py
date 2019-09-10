# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

# get version from __version__ variable in self_custom/__init__.py
from self_custom import __version__

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="self_custom",
    version=__version__,
    description="Customizations for SELF",
    author="Libermatic",
    author_email="info@libermatic.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
