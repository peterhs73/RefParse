#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from refparse import utils
from unittest.mock import Mock
from bs4 import BeautifulSoup


def test_filter_month_abbr():
    """Test Filter.month_abb"""

    assert utils.Filters.month_abbr("") == ""
    assert utils.Filters.month_abbr("01") == "Jan"
    assert utils.Filters.month_abbr(1) == "Jan"


def test_filter_month_name():
    """Test Filter.month_abb"""

    assert utils.Filters.month_name("") == ""
    assert utils.Filters.month_name("01") == "January"
    assert utils.Filters.month_name(1) == "January"


def test_get_attr():
    """Test get_attr for nested attributes"""
    nested = Mock(attr1="test", spec="attr1")
    test_obj = Mock(attr2=nested, spec="attr2")

    assert utils.get_attr(test_obj, "attr2/attr1") == "test"
    assert utils.get_attr(test_obj, "attr1/attr3").string == ""


def test_get_string():
    """Test get_attr for nested attributes"""
    html = "<body><test>   Hello world \n </test></body>"
    soup = BeautifulSoup(html, 'xml')
    assert utils.get_string(soup, "body/test") == "Hello world"


def test_empty():
    """Test the Empty class"""
    empty = utils.Empty()
    assert empty.string == ""
    assert empty.get_text(strip=True) == ""


def test_html_convert():
    """Test the html_covert function"""
    html_string = """<body><b>hello</b>
    world<sub>2</sub>
    <random>!</random>
    </body>
    """
    soup = BeautifulSoup(html_string, "xml").body
    plain, latex, html = utils.html_convert(soup)
    assert plain == "hello world2 !"
    assert latex == "\\textbf{hello} world\\textsubscript{2} !"
    assert html == "<b>hello</b> world<sub>2</sub> <random>!</random>"
