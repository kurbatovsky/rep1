# coding: utf8
"""
Find flight
"""
import sys
import re
import requests
from lxml import html
# arg parse


class Parser:
    """ Parser class """

    html = ''
    page = ''
    url = ''
    data = {}

    def __init__(self):
        """ Initialization """
        if len(sys.argv) >= 4:
            self.data = {'_ajax[templates][]': 'main',
                         '_ajax[requestParams][departure]': sys.argv[1],
                         '_ajax[requestParams][destination]': sys.argv[2],
                         '_ajax[requestParams][outboundDate]': sys.argv[3],
                         '_ajax[requestParams][returnDate]': sys.argv[4] if len(sys.argv) == 5 else '',
                         '_ajax[requestParams][adultCount]': '1',
                         '_ajax[requestParams][childCount]': '0',
                         '_ajax[requestParams][infantCount]': '0',
                         '_ajax[requestParams][returnDeparture]': '',
                         '_ajax[requestParams][returnDestination]': '',
                         '_ajax[requestParams][openDateOverview]': '',
                         '_ajax[requestParams][oneway]': '' if len(sys.argv) == 5 else 1}
        self.lines = {'outbound': [], 'return': []}
        self.construct_url()
        self.get_page()
        self.get_html()
        self.get_line()
        self.get_line(way='return')

    def construct_url(self):
        """ Construct url """
        url = 'https://www.flyniki.com/ru/booking/flight/vacancy.php?departure={0}&destination' \
              '={1}&outboundDate={2}'
        url_add = '&returnDate={0}'
        url_oneway = '&oneway={0}&openDateOverview=0' \
                     '&adultCount=1'
        args = sys.argv[1:]
        self.url = url.format(args[0], args[1], args[2]) + url_add.format(args[3]) + url_oneway.format(0) \
            if len(args) == 4 else url.format(args[0], args[1], args[2]) + url_oneway.format(1)

    def get_page(self):
        """ Get page """
        with requests.session() as sess:
            request = sess.get(self.url)
            post = sess.post(request.url, data=self.data)
            self.page = post.text

    def get_html(self):
        """ Get HTML """
        self.html = re.sub(r'\\', '', eval(self.page)['templates']['main'])

    def parse_html(self, xpath):
        """ Parse HTML """
        tree = html.fromstring(self.html)
        return tree.xpath(xpath)

    def get_line(self, way="outbound"):
        """ Get line from HTML """
        j = 1
        while True:
            for i in range(5, 9):
                xpath = 'string(//div[@class="{0} block"]//table/tbody/tr[{1}]/td[{2}]/label/div/span/@title)'
                line = self.parse_html(xpath.format(way, 2*j - 1, i))
                self.lines[way].append(line)
            j += 1
            last = len(self.lines[way]) - 1
            if last > 2:
                if self.lines[way][last] == '' and\
                                self.lines[way][last - 1] == '' and\
                                self.lines[way][last - 2] == '' and\
                                self.lines[way][last - 3] == '':
                    break


if __name__ == "__main__":
    print("Outbound:")
    print('\n'.join([x for x in Parser().lines['outbound'] if x != '']))
    print("Return:")
    print('\n'.join([x for x in Parser().lines['return'] if x != '']))

