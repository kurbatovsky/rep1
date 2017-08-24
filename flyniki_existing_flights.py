# coding: utf8
"""
Find existing flights for all airports
"""
import os
import requests


class AllFlights:
    """ Get all flights for each airports from flyniki """
    def __init__(self):
        self.all_airports = []
        self.all_ways = {}

    def get_airports(self, is_destination=False):
        url = 'https://www.flyniki.com/ru/site/json/suggestAirport.php'
        with requests.session() as sess:
            if not is_destination:
                request = sess.get(url, params=self.form_options())
                json = request.json()["suggestList"]
                for i in range(len(json)):
                    self.all_airports.append(json[i]["code"])
            else:
                for way in self.all_ways:
                    request = sess.get(url, params=self.form_options(way['departure']))
                    json = request.json()["suggestList"]
                    for i in range(len(json)):
                        way['destinations'].append(json[i]["code"])

    def construct_ways(self):
        """ Construct ways list """
        self.all_ways = [{'departure': x, 'destinations':[]} for x in self.all_airports]

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
        self.construct_ways()
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


def main():
    """ Main function """
    try:
        os.mkdir("Flights")
    except WindowsError:
        pass
    flights = AllFlights()
    flights.search_for_all_ways()
    write_in_files(flights.all_ways)
    output(flights.all_ways)
    flights.list_to_dict()

if __name__ == '__main__':
    main()
