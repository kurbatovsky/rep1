# coding: utf8
"""
Find existing flights for all airports
"""
import os
import argparse
import requests


class AllFlights:
    """ Get all flights for each airports from flyniki """
    def __init__(self):
        self.all_airports = []
        self.all_ways = {}

    def get_airports(self, is_destination=False):
        with requests.session() as sess:
            if not is_destination:
                self.all_airports = list(iata for iata in self.get_airports_from_json(sess, self.form_options()))
            else:
                self.all_ways = [{'departure': iata, 'destinations': []} for iata in self.all_airports]
                for way in self.all_ways:
                    way['destinations'] = list(iata for iata in self.get_airports_from_json(sess, self.form_options(way['departure'])))

    @staticmethod
    def get_airports_from_json(sess, params):
        result = list()
        url = 'https://www.flyniki.com/ru/site/json/suggestAirport.php'
        request = sess.get(url, params=params)
        json = request.json()["suggestList"]
        for iata in json:
            yield iata["code"]

    @staticmethod
    def form_options(code=''):
        """ For options """
        return {'searchfor': 'destinations' if code else 'departures',
                'searchflightid': 0,
                'departures[]': code,
                'destinations[]': '' if code else 'Город, Аэропорт',
                'suggestsource[0]': 'activeairports',
                'withcountries': 0,
                'withoutroutings': 0,
                'promotion[id]': '',
                'promotion[type]': '',
                'get_full_suggest_list': 'true' if code else '',
                'routesource[0]': 'airberlin',
                'routesource[1]': 'partner'}

    def search_for_all_ways(self):
        self.get_airports()
        self.get_airports(is_destination=True)

    def list_to_dict(self):
        result = {}
        for way in self.all_ways:
            result[way['departure']] = way['destinations']
        return result


def output(ways):
    """ Output function """
    for way in ways:
        print("From {} to:".format(way['departure']))
        print(' '.join(way['destinations']))
        print('\n\n')


def write_in_files(ways):
    for way in ways:
        with open(os.path.abspath(os.curdir) + '\\Flights\{}.txt'.format(way['departure']), 'w') as flights_file:
            for destination in way['destinations']:
                flights_file.write(destination + '\n')


def refresh():
    flights = AllFlights()
    flights.search_for_all_ways()
    write_in_files(flights.all_ways)
    output(flights.all_ways)


def main():
    """ Main function """
    if not os.path.exists("Flights"):
        os.mkdir("Flights")
        refresh()

if __name__ == '__main__':
    main()
