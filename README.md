# RefParse

The RefParse is a simple citation generation tool for doi and arXiv articles. It provides both a graphical and a command-line interface.

The API is a combination of the crossref REST API and arXiv API. The format template is in Cheetah3 format. See [RefParse wiki](https://github.com/peterhs73/RefParse/wiki) for more detailed description on API, user interface, and custom format templates.

![RefParse GUI](https://media.giphy.com/media/UUCJ18cy0gQPT7MM73/giphy.gif)

Installation (at the root directory) run

	```pip install . -e```

To test the package (at the root directory) run

	```tox```
