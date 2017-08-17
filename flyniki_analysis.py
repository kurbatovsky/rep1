# coding: utf8
"""
Find flight
"""
import re
import argparse
from datetime import date, datetime, timedelta
import itertools
import requests
from lxml import html


class Parser(object):
    """ Parser class """

    html = ''
    url = 'https://www.flyniki.com/ru/booking/flight/vacancy.php'
    data = {}

    def __init__(self):
        """ Initialization """
        self.args = self.parse_args()
        self.options = {}
        self.currency = ''
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
        self.combinations = []
        self.form_options()
        self.get_html()
        self.get_line()
        self.get_line(way='return')
        self.get_combinations()
        self.set_total_cost()
        self.clean_line_from_combinations()
        self.get_currency()

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
        assert re.match(
            r'^[A-Z]{3}$',
            self.args.outbound).group() == self.args.outbound, "IATA must be in AAA format"
        assert re.match(
            r'^[A-Z]{3}$',
            self.args.return_).group() == self.args.return_, "IATA must be is AAA format"
        assert self.is_correct_args(self.args.departure_date), "Incorrect departure date"
        if self.args.return_date != '':
            assert self.is_correct_args(self.args.return_date), "Incorrect return date"
            assert datetime.strptime(self.args.return_date, "%Y-%m-%d") >\
                   datetime.strptime(self.args.departure_date, "%Y-%m-%d") is True,\
                "Return date must be after departure date"

    @staticmethod
    def is_correct_args(date_):
        """ Check date """
        today = date.today()
        return today < datetime.strptime(date_, "%Y-%m-%d").date() < today + timedelta(days=355)

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
        data = {'_ajax[templates][]': 'main',
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
        with requests.session() as sess:
            request = sess.get(self.url, params=self.options)
            post = sess.post(request.url, data=data)
            try:
                self.html = post.json()['templates']['main']
            except KeyError:
                self.html = post.json()['errorRAW'][0]['code']

    def get_line(self, way="outbound"):
        """ Get line from HTML """
        tree = html.fromstring(self.html)
        xpath = '//div[@class="{0} block"]//tr[@role="group"]'
        for tr in tree.xpath(xpath.format(way)):
            self.lines[way].extend(tr.xpath('td[@role="radio"]//label/div[@class="lowest"]/span/@title'))
        if not self.lines[way]:
            self.lines[way].append('No flights found')

    @staticmethod
    def get_price(line):
        """ Get price from line """
        try:
            return float(re.sub(r',', '.', re.sub(r'\.', '', re.search(r'\d*\.\d*,\d*', line).group())))
        except AttributeError:
            return 0

    @staticmethod
    def by_price(tup):
        """ Function for sort """
        return float(tup[2])

    def get_combinations(self):
        """ Return all combinations of outbound and return flights """
        self.combinations = list(itertools.product(self.lines['outbound'], self.lines['return']))

    @staticmethod
    def total_cost(tup):
        """ Return total cost of outbound and return flights """
        return str(Parser.get_price(tup[0]) + Parser.get_price(tup[1]))

    def set_total_cost(self):
        """ Set total cost in combinations list """
        for i in range(len(self.combinations)):
            self.combinations[i] = self.combinations[i] + (self.total_cost(self.combinations[i]), )

    @staticmethod
    def clean_line(line):
        """ Delete price from line """
        return re.sub(r': \d*\.\d*,\d*', '', line)

    def clean_line_from_combinations(self):
        """ Delete all prices from combinations """
        for i in range(len(self.combinations)):
            self.combinations[i] = (self.clean_line(self.combinations[i][0]), self.clean_line(self.combinations[i][1]), self.combinations[i][2])

    def get_currency(self):
        """ get currency from HTML """
        tree = html.fromstring(self.html)
        xpath = '//div[@class="outbound block"]//thead/tr[2]/th[4]/text()'
        try:
            self.currency = tree.xpath(xpath)[0]
        except:
            pass


if __name__ == "__main__":
    FLIGHT = Parser()
    if FLIGHT.args.return_date != '':
        print("Combinations:\n" + '{0}\n'.join(['  —   '.join(x) for x in sorted(FLIGHT.combinations, key=Parser.by_price)]).format(FLIGHT.currency) + FLIGHT.currency)
    else:
        print("Outbound:\n" + '{0}\n'.join(sorted(FLIGHT.lines['outbound'], key=Parser.get_price)).format(FLIGHT.currency) + FLIGHT.currency)
