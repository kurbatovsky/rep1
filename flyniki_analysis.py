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
        '_ajax[requestParams][returnDate]': sys.argv[4],
        '_ajax[requestParams][adultCount]': '1',
        '_ajax[requestParams][childCount]': '0',
        '_ajax[requestParams][infantCount]': '0',
        '_ajax[requestParams][returnDeparture]': '',
        '_ajax[requestParams][returnDestination]': '',
        '_ajax[requestParams][openDateOverview]': '',
        '_ajax[requestParams][oneway]': ''}


class Flight:
    """ Flight class"""
    def __init__(self, departure, destination, duration, class_, min_price, max_price, is_back):
        """ Initialization """
        print("__init__")
        self.departure = departure
        self.destination = destination
        self.duration = duration
        self.class_ = class_
        self.min_price = min_price
        self.max_price = max_price
        self.is_back = is_back

    def show_flight(self):
        """ Show flight in cmd """
        print("show_flight")
        text = '{0}-{1} {2} {3}-{4} RUB {5}'
        print(text.format(self.departure, self.destination,
                          self.duration, self.min_price,
                          self.max_price, self.class_))


def construct_url():
    """ Construct url """
    print("construct_url")
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
    print("get_page")
    with requests.session() as sess:
        request = sess.get(construct_url())
        post = sess.post(request.url, data=DATA)
        return post


def get_html():
    """ Get HTML """
    print("get_html")
    html_ = re.sub(r'\\', '', eval(get_page().text)['templates']['main'])
    return html_


def parse_html(xpath):
    """ Parse HTML """
    print("parse_html")
    tree = html.fromstring(get_html())
    return tree.xpath(xpath)


def get_info(class_):
    """ Get information about flight """
    print("get_info")
    # [[Время вылета, время прибытия, время вылета назад, время прибытия назад], ...]
    # [[Длительность полёта, Длительность полёта назад], ...]
    # Наименование класса
    # [[Минимальная цена, Максимальная цена, Минимальная цена назад, Максимальная цена назад], ...]
    info = {'price': get_price(class_),
            'time': get_time(),
            'duration': get_duration(),
            'class': class_}
    return info


def get_time():
    """ Get time from HTML """
    print("get_time")
    departure = []
    for i in range(6):
        print(i)
        departure.append(parse_html('//*[@id="flightDepartureFi_{0}"]/time'.format(str(i))))
    return departure


def get_duration():
    """ Get duration from HTML """
    print("get_duration")
    duration = []
    for i in range(6):
        print(i)
        duration.append(parse_html('//*[@id="flightDurationFi_{0}"]'.format(i)))
    return duration


def get_price(class_):
    """ Get price from HTML """
    print("get_price")
    xpath = '//*[@class="fare faregrouptoggle {0} {1} flightfi_{2} bgcolor-{3}"]//span'
    price = []
    for i in range(6):
        print(i)
        i += 1
        price.append(parse_html(xpath.format(class_[:3], class_[4:], i, class_)))
    return price


def info_flight(class_, is_back=False):
    """ Print flights information"""
    print("info_flight")
    info = get_info(class_)
    if not is_back:
        flying = []
        for i in range(len(info['time'])):
            flying.append(Flight(info['time'][i][0].text, info['time'][i][1].text,
                                 info['duration'][i][0].text, info['class'],
                                 info['price'][i][0].text, info['price'][i][1].text, False))
        flying.sort(key=sort_by_time)
        for fly in flying:
            fly.show_flight()
    else:
        flying = []
        for i in range(len(info['time'])):
            flying.append(Flight(info['time'][i][2].text, info['time'][i][3].text,
                                 info['duration'][i][1].text, info['class'],
                                 info['price'][i][2].text, info['price'][i][3].text, True))
            flying.sort(key=sort_by_time)
        for fly in flying:
            fly.show_flight()


def sort_by_time(flight):
    """ Sort by time """
    print("sort_by_time")
    return flight.departure


def main():
    """ Main function """
    print("Direct flights:")
    info_flight("ECO_SAVER")
    info_flight("ECO_FLEX")
    info_flight("BUS_SAVER")
    info_flight("BUS_FLEX")
    """if len(sys.argv) == 5:
        print("Return flight:")
        info_flight("ECO_SAVER", is_back=True)
        info_flight("ECO_FLEX", is_back=True)
        info_flight("BUS_SAVER", is_back=True)
        info_flight("BUS_FLEX", is_back=True)"""


if __name__ == "__main__":
    main()
