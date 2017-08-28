# coding: utf8
"""
Find existing flights for all airports
"""
import os.path
import argparse
import requests


class AllFlights(object):
    """ Get all flights for each airports from flyniki """
    def __init__(self):
        """ Object initialization """
        self.all_airports = []
        self.all_ways = {}

    def get_airports(self, is_destination=False):
        """ Get airports"""
        with requests.session() as sess:
            if not is_destination:
                self.all_airports = list(iata for iata in self.get_airports_from_json(sess, self.form_options()))
            else:
                self.all_ways = [{'departure': iata, 'destinations': []} for iata in self.all_airports]
                for way in self.all_ways:
                    way['destinations'] = list(iata for iata in self.get_airports_from_json(sess, self.form_options(way['departure'])))

    @staticmethod
    def get_airports_from_json(sess, params):
        """ Get airports from json """
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
        """ Search for all ways """
        self.get_airports()
        self.get_airports(is_destination=True)

    def list_to_dict(self):
        """ Transform all_ways from list to dict """
        result = {}
        for way in self.all_ways:
            result[way['departure']] = way['destinations']
        return result

    def check_way(self, info):
        self.search_for_all_ways()
        all_ways = self.list_to_dict()
        return info.return_airport in all_ways[info.outbound_airport]


def output(ways):
    """ Output function """
    for way in ways:
        print("From {} to:".format(way['departure']))
        print(' '.join(way['destinations']))
        print('\n\n')


def write_in_files(ways):
    """ Write ways in files"""
    for way in ways:
        with open(os.path.join(os.path.abspath(os.curdir), 'Flights', '{}.txt'.format(way['departure'])), 'w') as flights_file:
            for destination in way['destinations']:
                flights_file.write(destination + '\n')


def refresh():
    """ Refresh info """
    flights = AllFlights()
    flights.search_for_all_ways()
    write_in_files(flights.all_ways)
    output(flights.all_ways)


def parse_args():
    """ Parse args """
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--refresh', help="refresh information")
    args = parser.parse_args()
    return args


def main():
    """ Main function """
    if parse_args().refresh:
        files = os.listdir("Flights")
        for file in files:
            os.remove(os.path.join(os.path.abspath(os.curdir), 'Flights', file))
        os.rmdir("Flights")
    if not os.path.exists("Flights"):
        os.mkdir("Flights")
        refresh()

if __name__ == '__main__':
    main()
