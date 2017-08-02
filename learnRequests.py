import sys
import requests
import lxml.html


HTTPS = "https://yandex.ru/search/"


def get_html(params):
    super_link = HTTPS + "?text=" + '%20'.join(params) + "&lr=47"
    req = requests.get(HTTPS, "text=" + '%20'.join(params) + "&lr=47")
    link = req.url
    if super_link != link:
        capcha_link = parse_html(req.text, "/html/body/div[2]/div/div[2]/div[2]/form/img/@src")[0]
        print("Capcha:", capcha_link)
        download_capcha(capcha_link)
        return '<body/>'
    else:
        return requests.get(HTTPS, "text=" + '%20'.join(params) + "&lr=47").text


def parse_html(html, xpath):
    tree = lxml.html.fromstring(html)
    return tree.xpath(xpath)


def download_capcha(link):
    with open("pics.txt", 'w+') as number_file:
        number = int(number_file.read())
        number += 1
        number_file.write(str(number))
    pic = requests.get(link)
    with open("img{}.jpg".format(number), "wb") as out:
        out.write(pic.content)


if __name__ == "__main__":
    html = get_html(sys.argv[1:])
    if parse_html(html, "/html/body/div[2]/div[1]/div[3]/div[1]/div[1]/ul/li[2]/div/div[1]/div[1]/a[2]/@href"):
        print(parse_html(html, "/html/body/div[2]/div[1]/div[3]/div[1]/div[1]/ul/li[2]/div/div[1]/div[1]/a[2]/@href"))



