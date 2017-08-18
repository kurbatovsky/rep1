# coding: utf8
"""
Find flight
"""
import re
import argparse
from datetime import date, datetime, timedelta
import itertools
from collections import *
import requests
from lxml import html


class Parser(object):
    """ Parser class """

    def __init__(self, args):
        """ Initialization """
        self.args = args
        self.tree = ''
        self.currency = ''
        self.lines = {'outbound': [], 'return': []}
        self.flights_combinations = []
        self.init_variables()

    def init_variables(self):
        """ Variables initialization """
        try:
            self.get_html()
        except KeyError:
            print("Flights not found")
            exit(0)
        self.get_line()
        if self.args.return_date:
            self.get_line(way='return')
        self.get_flights_combinations()
        self.set_total_cost()
        self.clean_line_from_combinations()
        self.get_currency()

    def form_options(self):
        """ Form options """
        return {'departure': self.args.outbound_airport,
                'destination': self.args.return_airport,
                'outboundDate': self.args.outbound_date,
                'oneway': '' if self.args.return_date else 1,
                'returnDate': self.args.return_date,
                'openDateOverview': '0',
                'adultCount': 1}

    def get_html(self):
        """ Get page """
        data = {'_ajax[templates][]': 'main',
                '_ajax[requestParams][departure]': self.args.outbound_airport,
                '_ajax[requestParams][destination]': self.args.return_airport,
                '_ajax[requestParams][outboundDate]': self.args.outbound_date,
                '_ajax[requestParams][returnDate]': self.args.return_date,
                '_ajax[requestParams][adultCount]': '1',
                '_ajax[requestParams][childCount]': '0',
                '_ajax[requestParams][infantCount]': '0',
                '_ajax[requestParams][returnDeparture]': '',
                '_ajax[requestParams][returnDestination]': '',
                '_ajax[requestParams][openDateOverview]': '',
                '_ajax[requestParams][oneway]': '' if self.args.return_date else 1}
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
            print('No flights found')
            exit(0)

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
        self.flights_combinations = list(itertools.product(self.lines['outbound'],
                                                           self.lines['return']))

    def calculate_total_cost(self, tuple_with_flights):
        """ Return total cost of outbound and return flights """
        return str(sum(map(self.get_price_from_string, tuple_with_flights)))

    def set_total_cost(self):
        """ Set total cost in combinations list """
        self.flights_combinations = [x + (self.calculate_total_cost(x), ) for x in self.flights_combinations]

    @staticmethod
    def clean_line(line):
        """ Delete price from line """
        return re.sub(r': \d+,\d+', '', line)

    def clean_line_from_combinations(self):
        """ Delete all prices from combinations """
        self.flights_combinations = list(map(lambda x: (self.clean_line(x[0]),
                                                        self.clean_line(x[1]),
                                                        x[2]), self.flights_combinations))

    def get_currency(self):
        """ Get currency from HTML """
        xpath = '//div[@class="outbound block"]//thead/tr[2]/th[4]/text()'
        self.currency = self.tree.xpath(xpath)[0]


def check_args(args):
    """ Check args """
    try:
        if re.match(r'^[A-Z]{3}$', args.outbound_airport).group() != args.outbound_airport:
            print("IATA must be in AAA format")
            return False
        elif re.match(r'^[A-Z]{3}$', args.return_airport).group() != args.return_airport:
            print("IATA must be in AAA format")
            return False
    except AttributeError:
        print("IATA must be in AAA format")
        return False
    if not is_correct_date(args.outbound_date):
        print("Date must be in YYYY-MM-DD format")
        return False
    if args.return_date != '':
        if not is_correct_date(args.return_date):
            print("Date must be in YYYY-MM-DD format")
            return False
    return True


def is_correct_date(flight_date):
    """ Check date """
    today = date.today()
    try:
        return today < datetime.strptime(flight_date, "%Y-%m-%d").date() < today + timedelta(days=355)
    except ValueError:
        return False


def parse_args():
    """ Parse args """
    parser = argparse.ArgumentParser()
    parser.add_argument('outbound_airport', help="start IATA")
    parser.add_argument('return_airport', help="finish IATA")
    parser.add_argument('departure_date', help="Departure date")
    parser.add_argument('return_date', nargs='?', help="Return date", default='')
    args = parser.parse_args()
    return args


def main():
    """ Main function """
    Flight_info = namedtuple('Flight_info', ['outbound_airport', 'return_airport', 'outbound_date', 'return_date'])
    args = parse_args()
    info = Flight_info(outbound_airport=args.outbound_airport,
                       return_airport=args.return_airport,
                       outbound_date=args.departure_date,
                       return_date=args.return_date)

    if not check_args(info):
        while True:
            print("String must be in AAA ZZZ YYYY-MM-DD [YYYY-MM-DD] format, try again")
            args = raw_input().split(' ')
            if len(args) == 3:
                args.append('')
            info = Flight_info(*args)
            if check_args(info):
                break
    flight = Parser(info)
    flight_lines_combinations = sorted(flight.flights_combinations if info.return_date else flight.lines['outbound'], key=flight.get_price_from_tuple if info.return_date else flight.get_price_from_string)
    flight_lines_combinations = ['  —   '.join(x) for x in flight_lines_combinations] if info.return_date else [re.sub(r',(?=\d)', '.', x) for x in flight.lines['outbound']]
    print("Combinations:\n" + '{0}\n'.join(flight_lines_combinations).format(flight.currency) + flight.currency)

if __name__ == "__main__":
    main()
