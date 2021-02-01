#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from refparse.api import RefAPI
from unittest.mock import patch, Mock
import logging
import os
import yaml

curpath = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(curpath, "..", "refparse", "config.yaml"), "r") as f:
    CONFIG = yaml.load(f, Loader=yaml.SafeLoader)


@patch("refparse.parser.requests.get")
def test_incorrect_reference(mock_get, caplog):
    """Test the RefAPI class when the reference is incorrect"""
    mock_get.return_value.ok = False

    RefAPI("random/url", {})
    assert caplog.record_tuples == [
        ("API", logging.ERROR, "random/url is not a valid doi or arXiv ID")
    ]


@patch("refparse.api.RefAPI.__init__", return_value=None)
def test_reference_matching(mock_refapi_init, caplog):
    """Test the reference_matching method for RefAPI"""

    assert RefAPI().match_reference("arXiv:hep-th/9901001v3") == (
        "hep-th/9901001v3",
        "arXiv",
    )
    assert RefAPI().match_reference("arXiv:1807.01219") == (
        "1807.01219",
        "arXiv",
    )
    assert RefAPI().match_reference(
        "http://dx.doi.org/10.1021/acs.jpcc.8b11783"
    ) == ("10.1021/acs.jpcc.8b11783", "crossref")

    assert RefAPI().match_reference("test/url") == ("test/url", "")
    assert caplog.record_tuples == [
        ("API", 40, "test/url is not a valid doi or arXiv ID")
    ]


BIBTEX = """@Article{Shi2010jul
  author = {Shi, Guanming., Chavas, Jean-paul., Stiegert, Kyle},
  title = {An Analysis of the Pricing of Traits in the U.S. Corn Seed Market},
  journal = {American Journal of Agricultural Economics},
  year = {2010},
  month = {jul},
  volume = {92},
  issue = {5},
  doi = {10.1093/ajae/aaq063},
  url = {http://doi.org/10.1093/ajae/aaq063},
  pages = {1324--1338}
  abstract = {}
}
"""

MD = (
    "[^Shi2010jul]: **Shi2010jul** Shi, Guanming., Chavas, Jean-paul., "
    'Stiegert, Kyle. "An Analysis of the Pricing of Traits in the U.S. '
    'Corn Seed Market". *American Journal of Agricultural Economics*, '
    "**2010**, *92*, 1324--1338 "
    "[10.1093/ajae/aaq063](http://doi.org/10.1093/ajae/aaq063).\n"
)

RST = (
    "..[#Shi2010jul] [**Shi2010jul**] Shi, Guanming., Chavas, Jean-paul., "
    'Stiegert, Kyle. "An Analysis of the Pricing of Traits in the U.S. '
    'Corn Seed Market". *American Journal of Agricultural Economics*, '
    "**2010**, *92*, 1324--1338 "
    "[`10.1093/ajae/aaq063 <http://doi.org/10.1093/ajae/aaq063>`__]\n"
)


TEXT = (
    "Shi2010jul Shi, Guanming., Chavas, Jean-paul., Stiegert, Kyle. "
    '"An Analysis of the Pricing of Traits in the U.S. Corn Seed Market". '
    "American Journal of Agricultural Economics, 2010, 92, 1324--1338 "
    "doi:10.1093/ajae/aaq063\n"
)


@patch("refparse.api.RefAPI.__init__", return_value=None)
def test_render_failure(mock_refapi_init, caplog):
    """Test the render method for RefAPI if the status is false"""
    api_obj = RefAPI()
    api_obj.status = False
    assert api_obj.render("") is None


@patch("refparse.api.RefAPI.__init__", return_value=None)
def test_render_default(mock_refapi_init, caplog):
    """Test the render method for RefAPI if the status is false"""
    api_obj = RefAPI()
    api_obj.status = True
    api_obj.format_template = CONFIG
    api_dict = {
        "doi": "10.1093/ajae/aaq063",
        "reference": "10.1093/ajae/aaq063",
        "ref_type": "doi",
        "url": "http://doi.org/10.1093/ajae/aaq063",
        "has_publication": True,
        "journal_full_title": "American Journal of Agricultural Economics",
        "journal_abbrev_title": "American Journal of Agricultural Economics",
        "author": [
            ["Shi", "Guanming"],
            ["Chavas", "Jean-paul"],
            ["Stiegert", "Kyle"],
        ],
        "title": (
            "An Analysis of the Pricing of "
            "Traits in the U.S. Corn Seed Market"
        ),
        "title_latex": (
            "An Analysis of the Pricing of "
            "Traits in the U.S. Corn Seed Market"
        ),
        "title_html": (
            "An Analysis of the Pricing of "
            "Traits in the U.S. Corn Seed Market"
        ),
        "abstract": "",
        "online_year": "2010",
        "online_month": "07",
        "online_day": "19",
        "has_print": True,
        "print_year": "2010",
        "print_month": "07",
        "print_day": "19",
        "pages": ["1324", "1338"],
        "volume": "92",
        "issue": "5",
    }
    api_obj.output = {}
    api_obj.parser = Mock(parsed=api_dict)

    assert api_obj.render("bibtex") == BIBTEX
    assert api_obj.render("md") == MD
    assert api_obj.render("rst") == RST
    assert api_obj.render("text") == TEXT
