#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Reference parser for different APIs"""


from refparse.utils import get_attr, get_string, html_convert
from bs4 import BeautifulSoup

import requests
import logging
from collections import defaultdict
import abc
from datetime import datetime
import re


class ParserBase(abc.ABC):
    """Abstract method for parsers

    If the attribute is not found, a empty string will be returned
    """

    REFNAME: str
    REF_URL: str
    QUERY_URL: str
    HEADER: dict

    def __init__(self, reference):

        self.log = logging.getLogger(self.__class__.__name__)
        self.query_url = self.QUERY_URL.format(reference)
        self.ok, self.text = self.request_text(self.query_url)
        self.parsed = defaultdict(str)

        if self.ok:
            # needs to use xml, abstract does not show up with lxml
            self.soup = BeautifulSoup(self.text, "xml")
            self.parsed[self.REFNAME] = reference
            self.parsed["reference"] = reference
            self.parsed["ref_type"] = self.REFNAME.replace(" ", "_")
            self.parsed["url"] = self.REF_URL.format(reference)
            # parse api
            self.parsed.update(self.parse_api(self.soup))

    def request_text(self, url):

        r = requests.get(
            url, headers={"Accept": "application/vnd.crossref.unixsd+xml"}
        )
        if r.ok:
            self.log.info(f"{self.REFNAME} found")
        elif r.status_code == 404 or r.status_code == 400:
            self.log.error(f"Incorrect {self.REFNAME}")
        elif r.status_code == 504:
            self.log.error(f"Gateway timeout, please try again")
        r.encoding = "utf-8"
        return r.ok, r.text

    @abc.abstractmethod
    def parse_api(self, soup):
        """The main function to parse api

        The method is required. This should be replaced for parsers
        """
        return {}


class CrossRefParser(ParserBase):

    REFNAME = "doi"
    REF_URL = "http://doi.org/{}"
    QUERY_URL = "http://dx.doi.org/{}"
    HEADER = {"Accept": "application/vnd.crossref.unixsd+xml"}

    def parse_api(self, soup):
        pdict = {}

        pdict["has_publication"] = True
        journal_meta = soup.journal_metadata
        pdict["journal_full_title"] = get_string(journal_meta, "full_title")
        pdict["journal_abbrev_title"] = get_string(
            journal_meta, "abbrev_title"
        )

        article_meta = soup.journal_article

        author = []
        author_tag = get_attr(article_meta, "contributors")
        for name in author_tag.find_all("person_name"):
            author.append([name.surname.string, name.given_name.string])
        pdict["author"] = author

        (
            pdict["title"],
            pdict["title_latex"],
            pdict["title_html"],
        ) = html_convert(get_attr(article_meta, "titles/title"))

        pdict["abstract"] = get_string(article_meta, "abstract")

        pub_online = article_meta.find(
            "publication_date", {"media_type": "online"}
        )
        pdict["online_year"] = get_string(pub_online, "year")
        pdict["online_month"] = get_string(pub_online, "month")
        pdict["online_day"] = get_string(pub_online, "day")

        pub_print = article_meta.find(
            "publication_date", {"media_type": "print"}
        )
        if pub_print:
            self.log.info("print version found")
            pdict["has_print"] = True
            pdict["print_year"] = get_string(pub_online, "year")
            pdict["print_month"] = get_string(pub_online, "month")
            pdict["print_day"] = get_string(pub_online, "day")

            first_page = get_string(soup, "pages/first_page")
            last_page = get_string(soup, "pages/last_page")
            pdict["pages"] = (
                [first_page, last_page] if last_page else [first_page]
            )

            issue_meta = soup.journal_issue
            pdict["volume"] = get_string(issue_meta, "journal_volume/volume")
            pdict["issue"] = get_string(issue_meta, "issue")
        else:
            pdict["has_print"] = False
        return pdict


class arXivParser(ParserBase):
    REF_URL = "http://arxiv.org/{}"
    QUERY_URL = "http://export.arxiv.org/api/query?id_list={}"
    REFNAME = "arXiv ID"
    HEADER = {}

    def search_doi(self, soup):
        """Check if the article has doi"""
        doi_tag = soup.find("link", {"title": "doi"})
        if doi_tag:
            self.log.warning(f"article has doi: {doi_tag['href']}")

    def parse_api(self, soup):
        """Parse the article information"""
        pdict = {}
        pdict["has_publication"] = False
        pdict["has_print"] = False
        self.search_doi(soup)

        article_meta = soup.entry
        # remove unnecessary 
        pdict["abstract"] = get_string(article_meta, "summary").replace(
            "\n", " "
        )
        print(repr(article_meta.summary.get_text(strip=True)))
        # sometimes the arXiv article title has unnecessary linebreak
        pdict["title"] = get_string(article_meta, "title").replace("\n ", "")
        pdict["title_latex"] = pdict["title"]

        pub_date = datetime.strptime(
            article_meta.updated.string, "%Y-%m-%dT%H:%M:%SZ"
        )
        pdict["online_year"] = str(pub_date.year)
        pdict["online_month"] = str(pub_date.month)
        pdict["online_day"] = str(pub_date.day)

        author = []
        for name in article_meta.find_all("name"):
            name_ = re.match(r"([\s\S]+) (\w+)", name.string)
            author.append([name_.group(2), name_.group(1)])
        pdict["author"] = author
        return pdict
