# coding: utf8
"""
Find existing flights for all airports
"""
import os.path
import argparse
import requests


def save(save_in="print", file_name=''):
    """ Save decorator """
    def my_decorator(a_function_to_decorate):
        """ Save decorator """
        name = '{}.txt'.format(a_function_to_decorate.__name__ if not file_name else file_name)
        path = os.path.join(os.path.abspath(os.curdir),
                            'Functions',
                            name)

        def wrapper(*args):
            """ Wrapper """
            result = a_function_to_decorate(*args)
            if save_in == "file":
                with open(path, 'a') as function_file:
                    function_file.write(str(result))
                    function_file.write('\n')
            elif save_in == "print":
                print result
            else:
                raise AttributeError

            return result
        return wrapper
    return my_decorator


class AllFlights(object):
    """ Get all flights for each airports from flyniki """

    def __init__(self):
        """ Object initialization """
        self.all_airports = []
        self.all_ways = {}

    def get_airports(self):
        """ Get airports"""
        with requests.session() as sess:
            self.all_airports = self.get_airports_from_json(sess, self.form_options())
            for iata in self.all_airports:
                self.all_ways[iata] = self.get_airports_from_json(sess, self.form_options(iata))

    @staticmethod
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

    def check_way(self, info):
        """ Check way exist """
        self.get_airports()
        return info.return_airport in self.all_ways[info.outbound_airport]


@save(save_in="file", file_name="Lolkek")
def output(ways):
    """ Output function """
    for way in ways.keys():
        print "From {} to:".format(way)
        print ' '.join(ways[way])
        print '\n\n'
    return "output"


def write_in_files(ways):
    """ Write ways in files"""
    for way in ways.keys():
        file_name = '{}.txt'.format(way)
        path = os.path.join(os.path.abspath(os.curdir), 'Flights', file_name)
        with open(path, 'a') as flights_file:
            flights_file.writelines('\n'.join(ways[way]))


@save(save_in="file", file_name="Lolkek")
def refresh():
    """ Refresh info """
    flights = AllFlights()
    flights.get_airports()
    write_in_files(flights.all_ways)
    output(flights.all_ways)
    return "refresh"


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
