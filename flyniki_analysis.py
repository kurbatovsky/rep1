# coding: utf8
"""
Find flight
"""
import sys
import re
import argparse
import requests
from lxml import html


class Parser:
    """ Parser class """

    html = ''
    page = ''
    url = ''
    data = {}

    def __init__(self):
        """ Initialization """
        self.args = self.parse_args()
        self.clean_args()
        self.data = {'_ajax[templates][]': 'main',
                     '_ajax[requestParams][departure]': self.args.outbound,
                     '_ajax[requestParams][destination]': self.args.return_,
                     '_ajax[requestParams][outboundDate]': self.args.departure_date,
                     '_ajax[requestParams][returnDate]': self.args.return_date,
                     '_ajax[requestParams][adultCount]': '1',
                     '_ajax[requestParams][childCount]': '0',
                     '_ajax[requestParams][infantCount]': '0',
                     '_ajax[requestParams][returnDeparture]': '',
                     '_ajax[requestParams][returnDestination]': '',
                     '_ajax[requestParams][openDateOverview]': '',
                     '_ajax[requestParams][oneway]': '' if self.args.return_date != '' else 1}
        self.lines = {'outbound': [], 'return': []}
        self.construct_url()
        self.get_page()
        self.get_html()
        self.get_line()
        self.get_line(way='return')

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('outbound', help="start IATA")
        parser.add_argument('return_', help="finish IATA")
        parser.add_argument('departure_date', help="Departure date")
        parser.add_argument('return_date', nargs='?', help="Return date", default='')
        return parser.parse_args()

    def clean_args(self):
        assert len(self.args.outbound) == 3, "IATA must be in AAA format"
        assert len(self.args.return_) == 3, "IATA must be is AAA format"
        assert self.is_correct_args(self.args.departure_date), "Incorrect departure date"
        if self.args.return_date != '':
            assert self.is_correct_args(self.args.return_date), "Incorrect return date"

    @staticmethod
    def is_correct_args(date):
        return 20170814 < int(re.sub(r'-', '', date)) < 20180809

    def construct_url(self):
        """ Construct url """
        url = 'https://www.flyniki.com/ru/booking/flight/vacancy.php?departure={0}&destination' \
              '={1}&outboundDate={2}'
        url_add = '&returnDate={0}'
        url_oneway = '&oneway={0}&openDateOverview=0' \
                     '&adultCount=1'
        self.url = url.format(self.args.outbound, self.args.return_, self.args.departure_date) +\
                   url_add.format(self.args.return_date) + url_oneway.format(0) \
            if self.args.return_date != '' else url.format(self.args.outbound,
                                                           self.args.return_,
                                                           self.args.departure_date) + url_oneway.format(1)

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

# BER JFK 2017-08-15 2017-08-19
if __name__ == "__main__":
    flights = Parser()
    print("Outbound:\n" + '\n'.join([x for x in flights.lines['outbound'] if x != '']))
    if flights.args.return_date != '':
        print("Return:\n" + '\n'.join([x for x in flights.lines['return'] if x != '']))

