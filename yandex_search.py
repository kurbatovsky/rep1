""" Download links from Yandex """
import sys
import requests
import lxml.html


HTTPS = "https://yandex.ru/search/"


def get_html(params):
    """ Get HTML from web"""
    request = requests.get(HTTPS, "text=" + "%20".join(params) + "&lr=47")
    print(request.url)
    return request.text


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
            xPath = "/html/body/div[2]/div[2]/div[3]/div[1]/div[1]/ul/li[{}]/h2/a/@href".format(i)
            link = parse_html(HTML, xPath)
        print(link)
