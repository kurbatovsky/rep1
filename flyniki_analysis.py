# coding: utf8
"""
Find flight
"""
import sys
import re
import requests
from lxml import html


DATA = {'_ajax[templates][]': 'main',
        '_ajax[requestParams][departure]': sys.argv[1],
        '_ajax[requestParams][destination]': sys.argv[2],
        '_ajax[requestParams][outboundDate]': sys.argv[3],
        '_ajax[requestParams][returnDate]': sys.argv[4] if len(sys.argv) == 5 else '',
        '_ajax[requestParams][adultCount]': '1',
        '_ajax[requestParams][childCount]': '0',
        '_ajax[requestParams][infantCount]': '0',
        '_ajax[requestParams][returnDeparture]': '',
        '_ajax[requestParams][returnDestination]': '',
        '_ajax[requestParams][openDateOverview]': '',
        '_ajax[requestParams][oneway]': '' if len(sys.argv) == 5 else 1}


class Flight:
    """ Flight class"""
    def __init__(self, departure, destination, duration, class_, min_price, max_price):
        """ Initialization """
        self.departure = departure.text
        self.destination = destination.text
        self.duration = duration.text
        self.class_ = class_
        self.min_price = min_price.text
        self.max_price = max_price.text

    def show_flight(self):
        """ Show flight in cmd """
        text = '{0}-{1} {2} {3}-{4} RUB {5}'
        print(text.format(self.departure, self.destination,
                          self.duration, self.min_price,
                          self.max_price, self.class_))


def construct_url():
    """ Construct url """
    url = 'https://www.flyniki.com/ru/booking/flight/vacancy.php?departure={0}&destination' \
          '={1}&outboundDate={2}'
    url_add = '&returnDate={0}'
    url_oneway = '&oneway={0}&openDateOverview=0' \
                 '&adultCount=1'
    args = sys.argv[1:]
    return url.format(args[0], args[1], args[2]) + url_add.format(args[3]) + url_oneway.format(0)\
        if len(args) == 4 else url.format(args[0], args[1], args[2]) + url_oneway.format(1)


def get_page():
    """ Get page """
    with requests.session() as sess:
        request = sess.get(construct_url())
        post = sess.post(request.url, data=DATA)
        return post


def get_html(page):
    """ Get HTML """
    html_ = re.sub(r'\\', '', eval(page.text)['templates']['main'])
    return html_


def parse_html(html_, xpath):
    """ Parse HTML """
    tree = html.fromstring(html_)
    return tree.xpath(xpath)


def get_info(html_, class_, back=False):
    """ Get information about flight """
    info = {'minimal': get_prices(html_, class_, back=back, current=False),
            'current': get_prices(html_, class_, back=back, current=True),
            'departure': get_time(html_, back=back, destination=False),
            'destination': get_time(html_, back=back, destination=True),
            'duration': get_durations(html_, back=back),
            'class': class_}
    return info


def set_direction(back):
    """ Check derection """
    return 3 if back else 1


def get_time(html_, back=False, destination=False):
    """ Get time from HTML"""
    times = []
    xpath = '//*[@id="flighttables"]/div[{0}]/div[2]//table[1]/tbody[1]/tr[{1}]/td[2]/span/time[{2}]'
    for i in range(1, 7):
        times.append(parse_html(html_, xpath.format(set_direction(back),
                                                    2*i - 1,
                                                    2 if destination else 1)))
    return times


def get_durations(html_, back=False):
    """ Get duration from HTML """
    durations = []
    xpath = '//*[@id="flighttables"]/div[{0}]/div[2]/table[1]/tbody[1]/tr[{1}]/td[4]/span'
    for i in range(1, 7):
        durations.append(parse_html(html_, xpath.format(set_direction(back), 2*i - 1)))
    return durations


def set_class(class_):
    """ Check class """
    return 5 if class_ == "ECO_SAVER" else 6 \
        if class_ == "ECO_FLEX" else 7 if class_ == "BUS_SAVER" else 8


def is_current(current):
    """ Check price """
    return 2 if current else 1


def get_prices(html_, class_, back=False, current=False):
    """ Get price fom HTML """
    xpath = '//*[@id="flighttables"]/div[{0}]/div[2]/table/tbody[1]/tr[{1}]/td[{2}]/label[1]/div[{3}]/span'
    prices = []
    for i in range(1, 7):
        prices.append(parse_html(html_, xpath.format(set_direction(back),
                                                     2*i - 1,
                                                     set_class(class_),
                                                     is_current(current))))
    return prices


def info_flight(info):
    """ Print flights information"""
    for i in range(len(info['departure'])):
        if info['departure'][i] != [] and info['destination'][i] != [] and info['duration'][i] != []\
                and info['minimal'][i] != [] and info['current'][i] != []:
            fly = Flight(info['departure'][i][0],
                         info['destination'][i][0],
                         info['duration'][i][0],
                         info['class'],
                         info['minimal'][i][0],
                         info['current'][i][0])
            fly.show_flight()
        else:
            continue


def sort_by_time(flight):
    """ Sort by time """
    return flight.departure


def main():
    """ Main function """
    args = sys.argv[1:]
    if len(args) >= 3:
        html_ = get_html(get_page())
        print("To {}".format(args[1]))
        info_flight(get_info(html_, class_="ECO_SAVER"))
        info_flight(get_info(html_, class_="ECO_FLEX"))
        info_flight(get_info(html_, class_="BUS_SAVER"))
        info_flight(get_info(html_, class_="BUS_FLEX"))
        if len(args) == 4:
            print("To {}".format(args[0]))
            info_flight(get_info(html_, class_="ECO_SAVER", back=True))
            info_flight(get_info(html_, class_="ECO_FLEX", back=True))
            info_flight(get_info(html_, class_="BUS_SAVER", back=True))
            info_flight(get_info(html_, class_="BUS_FLEX", back=True))
    else:
        print("Use format: flyniki_analysis.py IATA IATA YYYY-MM-DD [YYYY-MM-DD]")


if __name__ == "__main__":
    main()
