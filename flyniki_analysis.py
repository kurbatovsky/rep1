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

    def __init__(self):
        """ Initialization """
        self.args = ''
        self.tree = ''
        self.currency = ''
        self.lines = {'outbound': [], 'return': []}
        self.flights_combinations = []
        self.init_variables()

    def init_variables(self):
        self.args = self.parse_args()
        self.check_args()
        try:
            self.get_html()
        except KeyError:
            print("Flights not found")
            exit(0)
        self.get_line()
        if self.args.return_date != '':
            self.get_line(way='return')
        self.get_flights_combinations()
        self.set_total_cost()
        self.clean_line_from_combinations()
        self.get_currency()



    @staticmethod
    def parse_args():
        """ Parse args """
        parser = argparse.ArgumentParser()
        parser.add_argument('outbound_airport', help="start IATA")
        parser.add_argument('return_airport', help="finish IATA")
        parser.add_argument('departure_date', help="Departure date")
        parser.add_argument('return_date', nargs='?', help="Return date", default='')
        return parser.parse_args()

    def check_args(self):
        """ Clean args """
        try:
            assert re.match(r'^[A-Z]{3}$',
                            self.args.outbound_airport).group() == self.args.outbound_airport, "IATA must be is AAA format"
            assert re.match(
                r'^[A-Z]{3}$',
                self.args.return_airport).group() == self.args.return_airport, "IATA must be is AAA format"
        except AttributeError:
            raise AssertionError, "IATA must be is AAA format"
        assert self.is_correct_date(self.args.departure_date), "Incorrect departure date"
        if self.args.return_date != '':
            assert self.is_correct_date(self.args.return_date), "Incorrect return date"

    @staticmethod
    def is_correct_date(flight_date):
        """ Check date """
        today = date.today()
        try:
            return today < datetime.strptime(flight_date, "%Y-%m-%d").date() < today + timedelta(days=355)
        except ValueError:
            raise ValueError, "IATA must be is AAA format"

    def form_options(self):
        """ Form options """
        return {'departure': self.args.outbound_airport,
                'destination': self.args.return_airport,
                'outboundDate': self.args.departure_date,
                'oneway': '' if self.args.return_date != '' else 1,
                'returnDate': self.args.return_date,
                'openDateOverview': '0',
                'adultCount': 1}

    def get_html(self):
        """ Get page """
        data = {'_ajax[templates][]': 'main',
                '_ajax[requestParams][departure]': self.args.outbound_airport,
                '_ajax[requestParams][destination]': self.args.return_airport,
                '_ajax[requestParams][outboundDate]': self.args.departure_date,
                '_ajax[requestParams][returnDate]': self.args.return_date,
                '_ajax[requestParams][adultCount]': '1',
                '_ajax[requestParams][childCount]': '0',
                '_ajax[requestParams][infantCount]': '0',
                '_ajax[requestParams][returnDeparture]': '',
                '_ajax[requestParams][returnDestination]': '',
                '_ajax[requestParams][openDateOverview]': '',
                '_ajax[requestParams][oneway]': '' if self.args.return_date != '' else 1}
        url = 'https://www.flyniki.com/ru/booking/flight/vacancy.php'
        with requests.session() as sess:
            request = sess.get(url, params=self.form_options())
            post = sess.post(request.url, data=data)
            self.tree = html.fromstring(post.json()['templates']['main'])

    def get_line(self, way="outbound"):
        """ Get line from HTML """
        xpath = '//div[@class="{0} block"]//tr[@role="group"]'
        for tr in self.tree.xpath(xpath.format(way)):
            self.lines[way].extend(tr.xpath('td[@role="radio"]//label/div[@class="lowest"]/span/@title'))
        self.lines[way] = map(lambda x: re.sub(r'\.', '', x), self.lines[way])
        if not self.lines[way]:
            self.lines[way].append('No flights found')

    @staticmethod
    def get_price_from_string(line):
        """ Get price from line """
        try:
            return float(re.sub(r',', '.', re.search(r'\d+,\d+', line).group()))
        except AttributeError:
            return 0

    @staticmethod
    def get_price_from_tuple(tuple_with_flights):
        """ Function for sort """
        return float(tuple_with_flights[2])

    def get_flights_combinations(self):
        """ Return all combinations of outbound and return flights """
        self.flights_combinations = list(itertools.product(self.lines['outbound'], self.lines['return']))

    def calculate_total_cost(self, tuple_with_flights):
        """ Return total cost of outbound and return flights """
        return str(self.get_price_from_string(tuple_with_flights[0]) + self.get_price_from_string(tuple_with_flights[1]))

    def set_total_cost(self):
        """ Set total cost in combinations list """
        for i in range(len(self.flights_combinations)):
            self.flights_combinations[i] = self.flights_combinations[i] + (self.calculate_total_cost(self.flights_combinations[i]), )

    @staticmethod
    def clean_line(line):
        """ Delete price from line """
        return re.sub(r': \d+,\d+', '', line)

    def clean_line_from_combinations(self):
        """ Delete all prices from combinations """
        self.flights_combinations = list(map(lambda x: (self.clean_line(x[0]), self.clean_line(x[1]), x[2]), self.flights_combinations))

    def get_currency(self):
        """ get currency from HTML """
        xpath = '//div[@class="outbound block"]//thead/tr[2]/th[4]/text()'
        self.currency = self.tree.xpath(xpath)[0]

if __name__ == "__main__":
    FLIGHT = Parser()
    if FLIGHT.args.return_date != '':
        print("Combinations:\n" + '{0}\n'.join(['  —   '.join(x) for x in sorted(FLIGHT.flights_combinations, key=Parser.get_price_from_tuple)]).format(FLIGHT.currency) + FLIGHT.currency)
    else:
        print(re.sub(r',0', '.', "Outbound:\n" + '{0}\n'.join(sorted(FLIGHT.lines['outbound'], key=Parser.get_price_from_string)).format(FLIGHT.currency) + FLIGHT.currency))
