# RefParse [![Current Version](https://img.shields.io/badge/version-0.1.1-green.svg)](https://github.com/peterhs73/RefParse) [![](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/) [![License](https://img.shields.io/badge/License-BSD%202--Clause-orange.svg)](https://opensource.org/licenses/BSD-2-Clause)

The RefParse is a simple citation generation tool for doi and arXiv articles. It provides both a graphical and a command-line interface.

The API is a combination of the crossref REST API and arXiv API. The format template is in Cheetah3 format. See [RefParse wiki](https://github.com/peterhs73/RefParse/wiki) for more detailed description on API, user interface, and custom format templates.

![RefParse GUI](https://media.giphy.com/media/KVRz3bp64jxjN8HJis/giphy.gif)

## Quickstart

Installation from the newest release v0.1.1

	python -m pip install git+https://github.com/peterhs73/RefParse.git@v0.1.1#egg=RefParse


### Develop

Clone the package

    git clone https://github.com/peterhs73/RefParse.git

under the RefParse directory, install the package in editing mode

    pip install . -e

run tests

	tox

## Features
- Automatically determine if link is doi or arXiv ID
- Allow user customization for formatting
- Comes with custom filters for data handling

See wiki for more details

## Reference

- [RefParse wiki](https://github.com/peterhs73/RefParse/wiki)
- [Change Log](https://github.com/peterhs73/RefParse/blob/master/CHANGELOG.md)
- [Releases](https://github.com/peterhs73/RefParse/releases)
