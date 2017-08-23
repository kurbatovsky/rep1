# coding: utf8
"""
Find existing flights for all airports
"""
import requests


class AllFlights:
    """ Get all flights for each airports from flyniki """
    def __init__(self):
        self.all_airports = []
        self.all_ways = {}

    def get_airports(self):
        """ Get all airports """
        url = 'https://www.flyniki.com/ru/site/json/suggestAirport.php'
        with requests.session() as sess:
            request = sess.get(url, params=self.form_options())
            json = request.json()["suggestList"]
            for i in range(len(json)):
                self.all_airports.append(json[i]["code"])

    def construct_ways(self):
        """ Construct ways list"""
        self.all_ways = [{'departure': x, 'destinations':[]} for x in self.all_airports]

    def get_destination(self):
        """ Get all ways """
        url = 'https://www.flyniki.com/ru/site/json/suggestAirport.php'
        with requests.session() as sess:
            for way in self.all_ways:
                request = sess.get(url, params=self.form_destination_option(way['departure']))
                json = request.json()["suggestList"]
                for i in range(len(json)):
                    way['destinations'].append(json[i]["code"])

    @staticmethod
    def form_destination_option(code):
        """ Form options """
        return {'searchfor': 'destinations',
                'searchflightid': 0,
                'departures[]': code,
                'destinations[]': '',
                'suggestsource[0]': 'activeairports',
                'withcountries': 0,
                'withoutroutings': 0,
                'promotion[id]': '',
                'promotion[type]': '',
                'get_full_suggest_list': 'false',
                'routesource[0]': 'airberlin',
                'routesource[1]': 'partner'}

    @staticmethod
    def form_options():
        """ Form options """
        return {'searchfor': 'departures',
                'searchflightid': 0,
                'departures[]': '',
                'destinations[]': 'Город, Аэропорт',
                'suggestsource[0]': 'activeairports',
                'withcountries': 0,
                'withoutroutings': 0,
                'promotion[id]': '',
                'promotion[type]': '',
                'get_full_suggest_list': 'true',
                'routesource[0]': 'airberlin',
                'routesource[1]': 'partner'}


def output(ways):
    """ Output function """
    for way in ways:
        print("From {} to:".format(way['departure']))
        print(' '.join(way['destinations']))
        print('\n\n')


def main():
    """ Main function """
    flights = AllFlights()
    flights.get_airports()
    flights.construct_ways()
    flights.get_destination()
    output(flights.all_ways)

if __name__ == '__main__':
    main()
