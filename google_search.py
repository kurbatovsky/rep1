import sys
import re
import requests
import lxml.html


def clear_request(params):
    """ Create request """
    for param in params:
        param = re.sub(r'\W', '', param)
    return params


def get_page(params):
    """ Get page from request"""
    url = "https://google.ru/search"
    page = requests.get(url, "hp&q=" + "+".join(params))
    return page


def get_html(params):
    """ Get HTML from web"""
    page = get_page(clear_request(params))
    return page.text


def parse_html(html, xpath):
    """ Parse HTML """
    tree = lxml.html.fromstring(html)
    return tree.xpath(xpath)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        HTML = get_html(sys.argv[1:])
        xPath = "/html/body//div[2]//div/h3/a/@href"
        links = parse_html(HTML, xPath)
        linksQuantity = 0
        for link in links:
            if bool(re.match(r'^/search', link)):
                continue
            else:
                link = re.sub(r'/url\?q=', '', link)
                link = re.sub(r'&sa=.+', '', link)
                linksQuantity += 1
                print(link)
            if linksQuantity == 3:
                break
    else:
        print("Use format: 'python google_search.py *params'")
