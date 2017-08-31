# coding: utf8
"""
Find existing flights for all airports
"""
import os.path
import argparse
import requests


def save_in_file(a_function_to_decorate):
    def wrapper(*args):
        result = a_function_to_decorate(*args)
        with open(os.path.join(os.path.abspath(os.curdir), 'Functions', '{}.txt'.format(a_function_to_decorate.__name__)), 'a') as function_file:
            function_file.write(str(result))
            function_file.write('\n')
        return result
    return wrapper


class AllFlights(object):
    """ Get all flights for each airports from flyniki """

    @save_in_file
    def __init__(self):
        """ Object initialization """
        self.all_airports = []
        self.all_ways = {}

    @save_in_file
    def get_airports(self):
        """ Get airports"""
        with requests.session() as sess:
            self.all_airports = self.get_airports_from_json(sess, self.form_options())
            for iata in self.all_airports:
                self.all_ways[iata] = self.get_airports_from_json(sess, self.form_options(iata))

    @staticmethod
    @save_in_file
    def get_airports_from_json(sess, params):
        """ Get airports from json """
        url = 'https://www.flyniki.com/ru/site/json/suggestAirport.php'
        request = sess.get(url, params=params)
        json = request.json()["suggestList"]
        result = []
        for iata in json:
            result.append(iata["code"])
        return result

    @staticmethod
    @save_in_file
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

    @save_in_file
    def check_way(self, info):
        self.get_airports()
        all_ways = self.list_to_dict()
        return info.return_airport in all_ways[info.outbound_airport]

@save_in_file
def output(ways):
    """ Output function """
    for way in ways.keys():
        print("From {} to:".format(way))
        print(' '.join(ways[way]))
        print('\n\n')

@save_in_file
def write_in_files(ways):
    """ Write ways in files"""
    for way in ways.keys():
        with open(os.path.join(os.path.abspath(os.curdir), 'Flights', '{}.txt'.format(way)), 'a') as flights_file:
            flights_file.writelines('\n'.join(ways[way]))

@save_in_file
def refresh():
    """ Refresh info """
    flights = AllFlights()
    flights.get_airports()
    write_in_files(flights.all_ways)
    output(flights.all_ways)

@save_in_file
def parse_args():
    """ Parse args """
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--refresh', help="refresh information")
    args = parser.parse_args()
    return args

@save_in_file
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
