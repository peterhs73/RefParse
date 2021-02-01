# RefParse

The RefParse is a simple citation generation tool for doi and arXiv articles. It provides both a graphical and a command-line interface.

The API is a combination of the crossref REST API and arXiv API. The format template is in Cheetah3 format. See [RefParse wiki](https://github.com/peterhs73/RefParse/wiki) for the more detailed API description, user interface, and how to extend the custom format templates.  

![RefParse GUI](https://gph.is/g/aeo8GRk)

Installation (at the root directory) run

	```pip install . -e```

To test the package (at the root directory) run

	```tox```

