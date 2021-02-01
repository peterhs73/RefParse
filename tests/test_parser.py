#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from unittest.mock import patch
from refparse.parser import CrossRefParser, arXivParser, ParserBase
import os
import logging

curpath = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(curpath, "arXiv_test_example.xml"), "r") as f:
    ARXIV_XML = f.read()
with open(os.path.join(curpath, "crossref_test_example.xml"), "r") as f:
    DOI_XML = f.read()


class TestParser(ParserBase):
    __test__ = False
    """Empty parser to test on"""

    REFNAME = "TEST ID"
    QUERY_URL = "http://{}"
    REF_URL = "http://{}"
    HEADER = {}

    def parse_api(self):
        return {}


@patch("refparse.parser.requests.get")
def test_parser_false_status(mock_get, caplog):
    """Test response values and status

    A mock parser is crated, which does not parse the result
    """

    mock_get.return_value.text = ""
    mock_get.return_value.ok = False
    mock_get.return_value.status_code = 400
    TestParser("reference")

    mock_get.return_value.status_code = 504
    TestParser("reference")

    assert caplog.record_tuples == [
        ("TestParser", logging.ERROR, "Incorrect TEST ID"),
        ("TestParser", logging.ERROR, "Gateway timeout, please try again"),
    ]


# Test arXiv parser
@patch("refparse.parser.requests.get")
def test_arXiv_parser(mock_get, caplog):
    """Test arXiv parser with arXiv:hep-th/9901001v3"""
    mock_get.return_value.ok = True
    mock_get.return_value.text = ARXIV_XML

    parser = arXivParser("hep-th/9901001v3")

    api_dict = {
        "arXiv ID": "hep-th/9901001v3",
        "reference": "hep-th/9901001v3",
        "ref_type": "arXiv_ID",
        "url": "http://arxiv.org/hep-th/9901001v3",
        "has_publication": False,
        "has_print": False,
        "abstract": "We explicitly give the correspondence between spectra of "
        "heterotic string theory compactified on $T^2$ and string "
        "junctions in type IIB theory compactified on $S^2$.",
        "title": "String Junctions and Their Duals in Heterotic String Theory",
        "title_latex": "String Junctions and Their "
        "Duals in Heterotic String Theory",
        "online_year": "1999",
        "online_month": "5",
        "online_day": "10",
        "author": [["Imamura", "Yosuke"]],
    }

    assert parser.parsed == api_dict
    assert caplog.record_tuples == [
        (
            "arXivParser",
            logging.WARNING,
            "article has doi: http://dx.doi.org/10.1143/PTP.101.1155",
        )
    ]


@patch("refparse.parser.requests.get")
def test_crossref_parser(mock_get, caplog):
    """Test parsed CrossrefParser with doi: 10.1021/acs.jpcc.8b11783"""
    mock_get.return_value.ok = True
    mock_get.return_value.text = DOI_XML

    parser = CrossRefParser("10.1021/acs.jpcc.8b11783")

    api_dict = {
        "doi": "10.1021/acs.jpcc.8b11783",
        "reference": "10.1021/acs.jpcc.8b11783",
        "ref_type": "doi",
        "url": "http://doi.org/10.1021/acs.jpcc.8b11783",
        "has_publication": True,
        "journal_full_title": "The Journal of Physical Chemistry C",
        "journal_abbrev_title": "J. Phys. Chem. C",
        "author": [
            ["Tirmzi", "Ali Moeed"],
            ["Christians", "Jeffrey A."],
            ["Dwyer", "Ryan P."],
            ["Moore", "David T."],
            ["Marohn", "John A."],
        ],
        "title": (
            "Substrate-Dependent Photoconductivity Dynamics "
            "in a High-Efficiency Hybrid Perovskite Alloy"
        ),
        "title_latex": (
            "Substrate-Dependent Photoconductivity Dynamics "
            "in a High-Efficiency Hybrid Perovskite Alloy"
        ),
        "title_html": (
            "Substrate-Dependent Photoconductivity Dynamics "
            "in a High-Efficiency Hybrid Perovskite Alloy"
        ),
        "abstract": "",
        "online_year": "2019",
        "online_month": "01",
        "online_day": "17",
        "has_print": True,
        "print_year": "2019",
        "print_month": "01",
        "print_day": "17",
        "pages": ["3402", "3415"],
        "volume": "123",
        "issue": "6",
    }

    assert parser.parsed == api_dict
