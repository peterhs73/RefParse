#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="refparse",  # Replace with your own username
    version="0.1.0",
    author="Peter Sun",
    author_email="peterhs73@outlook.com",
    description="Parse DOI and arXiv reference",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pterhs73/RefParse",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pyyaml>=5.0",
        "Cheetah3>=3.2.6",
        "Click>=7.0",
        "PySide2>=5.0",
        "requests>=2.0",
        "pylatexenc>=2",
        "titlecase>=2.0",
        "beautifulsoup4>=4.0",
        "lxml>=4.0",
    ],
    entry_points={"console_scripts": ["refparse=refparse.refparse:cli"]},
    python_requires=">=3.6",
)
