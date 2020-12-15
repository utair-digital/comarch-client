#!/usr/bin/env python
from setuptools import setup, find_packages


requires = [
    "xmltodict~=0.12.0",
    "aiohttp~=3.6.2",
]


setup(
    name="comarch_client",
    version="0.3.0",
    description="comarch soap client",
    long_description=open("README.rst").read(),
    author="Utair",
    url="https://github.com/utair-digital/comarch-client",
    scripts=[],
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    extras_require={},
    license="GNU General Public License v3.0",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Framework :: AsyncIO",
    ],
)
