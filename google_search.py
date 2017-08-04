# -*- coding: utf-8 -*-
""" Download links from Google """
import sys
import re
import requests
from lxml import html


def clear_link(link):
    """ Clear link"""
    link = re.sub(r'/url\?q=', '', link)
    link = re.sub(r'&sa=.+', '', link)
    return link


def clear_request(params):
    """ Create request """
    return [re.sub(r'\W', '', param) for param in params]


def get_page(params):
    """ Get page from request"""
    url = "https://google.ru/search"
    page = requests.get(url, "hp&q=" + "+".join(params))
    return page


def get_html(params):
    """ Get HTML from web"""
    page = get_page(clear_request(params))
    return page.text


def parse_html(html_):
    """ Parse HTML """
    tree = html.fromstring(html_)
    return tree.xpath("/html/body//div[2]//div/h3/a/@href")


def is_valid(link):
    """ Link validation """
    if not re.match(r'/search', link):
        return clear_link(link)
    return None


def main():
    """ Main function """
    args = sys.argv[1:]
    if args:
        html_ = get_html(args)
        links = parse_html(html_)
        if links:
            print('\n'.join([is_valid(link) for link in links if is_valid(link)][:3]))
        else:
            print("No results")
    else:
        print("Use format: 'python google_search.py *params'")

if __name__ == "__main__":
    main()
