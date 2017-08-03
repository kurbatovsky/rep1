""" Download links from Yandex """
import sys
import re
import requests
import lxml.html


def get_page(params):
    """ Get page from request"""
    url = "https://yandex.ru/search/"
    page = requests.get(url, "text=" + "%20".join(params) + "&lr=47")
    return page


def get_html(params):
    """ Get HTML from web"""
    page = get_page(params)
    return page.text


def parse_html(html, xpath):
    """ Parse HTML """
    tree = lxml.html.fromstring(html)
    return tree.xpath(xpath)


if __name__ == "__main__":
    HTML = get_html(sys.argv[1:])
    for i in range(1, 4, 1):
        xPath = "/html/body/div[2]/div[2]/div[3]/div[1]/div[1]/ul/li[{}]/div/h2/a/@href".format(i)
        link = parse_html(HTML, xPath)
        if link is []:
            xPath = re.sub(r"div/", '', xPath)
            link = parse_html(HTML, xPath)
        print(link)
