#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Utility functions for parser and Cheetah3 templat"""


from pylatexenc.latexencode import unicode_to_latex
from calendar import month_abbr, month_name
from titlecase import titlecase
import re
import bs4
from collections import defaultdict


class Empty(object):
    """Use to create empty object

    Used as an placeholder for bs4 tag object.
    string and get_text method return empty strin"""

    string = ""

    def get_text(self, *args, **kwargs):
        return ""


def get_attr(obj, path):
    """Get nested attribute

    :param obj object/namedtuple: object to get the attribute
    :param path str: nested attribute path, separated by '/'
    """

    try:
        for p in path.split("/"):
            obj = getattr(obj, p)
        return obj
    except AttributeError:
        return Empty()


def get_string(obj, path):
    """Get the string attribute of nested object

    With strip=True, text with html tags around is be stripped away
    its white space around
    :param obj object/namedtuple: object to get the attribute
    :param path str: nested attribute path, separated by '/'
    """
    try:
        return get_attr(obj, path).get_text(strip=True)
    except AttributeError:
        return ""


def html_convert(tag_element):
    """extract the html content of the tag element

    Extract the html of the tag element, and present it as close
    as the browser. Currently this function is limited.

    :param tag_element bs4.element.tag: tag to extract content
        This should be a soup object
    """

    _html_to_latex_tags = defaultdict(lambda: ("", ""))
    _html_to_latex_tags.update(
        {
            "i": ("\\textit{", "}"),
            "b": ("\\textbf{", "}"),
            "strong": ("\\textbf{", "}"),
            "em": ("\\emph{", "}"),
            "u": ("\\underline{", "}"),
            "sub": ("\\textsubscript{", "}"),
            "sup": ("\\textsuperscript{", "}"),
        }
    )

    if tag_element is None:
        return "", "", ""

    content = []
    content_html = []
    content_latex = []
    tag_pattern = re.compile(r"<\w+\s*\w*>(.+)</(\w+)>")

    for ele in tag_element:
        if not isinstance(ele, bs4.element.Tag):
            str_ = re.sub(r"([\n].+[\n])\s+", r"\1", ele)
            str_ = re.sub(r"\s+", " ", str_.replace("\n", " "))
            content.append(str_)
            content_html.append(str_)
            content_latex.append(str_)
        else:
            subtag = re.match(tag_pattern, str(ele))
            text = subtag.group(1)
            tag = subtag.group(2)

            content.append(text)
            content_html.append(str(ele))
            latex = "{latex[0]}{text}{latex[1]}".format(
                latex=_html_to_latex_tags[tag], text=text,
            )
            content_latex.append(latex)
    return (
        "".join(content).strip(),
        "".join(content_latex).strip(),
        "".join(content_html).strip(),
    )


class Filters:
    """Filter used for Cheetah Template engine"""

    @classmethod
    def list(cls, *args, **kwargs):
        return list(*args, **kwargs)

    @classmethod
    def map(cls, *args, **kwargs):
        return map(*args, **kwargs)

    @classmethod
    def titlecase(cls, text):
        """A wrapper for titlecase function"""
        return titlecase(text)

    @classmethod
    def month_abbr(cls, month):
        """A wrapper for calendar.month_abbr

        :param month str: month string or int, empty string will
            be converted to 0, and return an empty string
        """
        month = int(month) if month else 0
        return month_abbr[month]

    @classmethod
    def month_name(cls, month):
        """A wrapper for calendar.month_name

        :param month str: month string or int, empty string will
            be converted to 0, and return an empty string
        """
        month = int(month) if month else 0
        return month_name[month]

    @classmethod
    def unicode_to_latex(cls, text):
        """A wrapper for calendar.month_name"""
        return unicode_to_latex(text)
