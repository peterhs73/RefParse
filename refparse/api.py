#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Main API class"""


from refparse.parser import CrossRefParser, arXivParser
from Cheetah.Template import Template
from refparse.utils import Filters
import logging
import re

api_logger = logging.getLogger("API")
api_method = {"crossref": CrossRefParser, "arXiv": arXivParser}


class RefAPI:
    """Abstract base class for user interaction

    For attribute that is None, empty string will be returned
    """

    def __init__(self, reference, format_template):
        """Initiate the object with different apis

        :param url string: the url of the target
        """

        cleaned_ref, api_type = self.match_reference(reference)
        if api_type:
            self.format_template = format_template
            self.parser = api_method[api_type](cleaned_ref)
            self.status = self.parser.ok
            self.output = {}
        else:
            self.status = False

    def match_reference(self, reference):
        """Match reference into either doi or arXiv ID

        The pattern for doi can be found on the API page
        arXiv ID has types, pre-2007 and post-2007
        Here the patterns are slightly modified to do a full search
        """
        doi_pattern = re.compile(r"10.\d{4,9}/[-._;()/:a-zA-Z0-9]+")
        arxiv_pattern1 = re.compile(r"\d{4}.\d{4,5}(v\d)?")
        arxiv_pattern2 = re.compile(r"[-a-z]+(.[A-Z]{2})?/\d{7}(v\d)?")

        if doi_pattern.search(reference):
            return doi_pattern.search(reference).group(0), "crossref"
        elif arxiv_pattern1.search(reference):
            return arxiv_pattern1.search(reference).group(0), "arXiv"
        elif arxiv_pattern2.search(reference):
            return arxiv_pattern2.search(reference).group(0), "arXiv"
        else:
            api_logger.error(f"{reference} is not a valid doi or arXiv ID")
            return reference, ""

    def render(self, ref_format):
        """Render the desired format

        If the ref_format is already rendered, it stores in the dictionary
        else it will render the format
        :param ref_format string: reference format
        """
        if not self.status:
            return
        elif ref_format not in self.output:

            template = self.format_template[ref_format]
            result = Template(
                template, searchList=[{"FN": Filters}, self.parser.parsed],
            )

            self.output[ref_format] = str(result)
        return self.output[ref_format]
