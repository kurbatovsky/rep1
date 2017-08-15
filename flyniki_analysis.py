# coding: utf8
"""
Find flight
"""
import re
import argparse
from datetime import date
import requests
from lxml import html


class Parser:
    """ Parser class """

    html = ''
    url = ''
    data = {}

    def __init__(self):
        """ Initialization """
        self.args = self.parse_args()
        self.options = {}
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
        self.form_options()
        self.get_html()
        self.get_line()
        self.get_line(way='return')

    @staticmethod
    def parse_args():
        """ Parse args """
        parser = argparse.ArgumentParser()
        parser.add_argument('outbound', help="start IATA")
        parser.add_argument('return_', help="finish IATA")
        parser.add_argument('departure_date', help="Departure date")
        parser.add_argument('return_date', nargs='?', help="Return date", default='')
        return parser.parse_args()

    def clean_args(self):
        """ Clean args """
        assert re.match(r'^[A-Z][A-Z][A-Z]$',
                        self.args.outbound).group() == self.args.outbound, "IATA must be in AAA format"
        assert re.match(r'^[A-Z][A-Z][A-Z]$',
                        self.args.return_).group() == self.args.return_, "IATA must be is AAA format"
        assert self.is_correct_args(self.args.departure_date), "Incorrect departure date"
        if self.args.return_date != '':
            assert self.is_correct_args(self.args.return_date), "Incorrect return date"

    @staticmethod
    def date_to_int(date_):
        """ Convert date to int """
        return int(re.sub(r'-', '', str(date_)))

    @staticmethod
    def is_correct_args(date_):
        """ Check date """
        today = date.today()
        return Parser.date_to_int(today) < Parser.date_to_int(date_) < Parser.date_to_int(today) + 10000

    def form_options(self):
        """ Form options """
        self.options = {'departure': self.args.outbound,
                        'destination': self.args.return_,
                        'outboundDate': self.args.departure_date,
                        'oneway': '' if self.args.return_date != '' else 1,
                        'returnDate': self.args.return_date,
                        'openDateOverview': '0',
                        'adultCount': 1}

    def get_html(self):
        """ Get page """
        with requests.session() as sess:
            request = sess.get('https://www.flyniki.com/ru/booking/flight/vacancy.php', params=self.options)
            post = sess.post(request.url, data=self.data)
            self.html = post.json()['templates']['main']

    def parse_html(self, xpath):
        """ Parse HTML """
        tree = html.fromstring(self.html)
        return tree.xpath(xpath)

    def get_line(self, way="outbound"):
        """ Get line from HTML """
        j = 1
        emptiness_counter = 0
        while emptiness_counter != 4:
            for i in range(5, 9):
                xpath = 'string(//div[@class="{0} block"]//table/tbody/tr[{1}]/td[{2}]/label/div/span/@title)'
                line = self.parse_html(xpath.format(way, 2*j - 1, i))
                if line == '':
                    emptiness_counter += 1
                else:
                    emptiness_counter = 0
                    self.lines[way].append(line)
            j += 1


if __name__ == "__main__":
    FLIGHT = Parser()
    print("Outbound:\n" + '\n'.join(FLIGHT.lines['outbound']))
    if FLIGHT.args.return_date != '':
        print("Return:\n" + '\n'.join(FLIGHT.lines['return']))
