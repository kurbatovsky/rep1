# coding: utf8
"""
Find flight
"""
import sys
import re
import requests
import codecs
from lxml import html
import argparse


DATA = {}
# arg parse


class Page:
    """ Page class """

    HTML = ''
    page = ''
    url = ''

    def __init__(self):
        pass

    @classmethod
    def get_html(cls):
        """ Get HTML """
        cls.HTML = re.sub(r'\\', '', eval(cls.get_page().text)['templates']['main'])

    @classmethod
    def get_page(cls):
        """ Get page """
        with requests.session() as sess:
            request = sess.get(cls.url)
            post = sess.post(request.url, data=DATA)
            return post

    @staticmethod
    def parse_html(xpath):
        """ Parse HTML """
        tree = html.fromstring(Page.HTML)
        return tree.xpath(xpath)

    @classmethod
    def construct_url(cls):
        """ Construct url """
        url = 'https://www.flyniki.com/ru/booking/flight/vacancy.php?departure={0}&destination' \
              '={1}&outboundDate={2}'
        url_add = '&returnDate={0}'
        url_oneway = '&oneway={0}&openDateOverview=0' \
                     '&adultCount=1'
        args = sys.argv[1:]
        cls.url = url.format(args[0], args[1], args[2]) + url_add.format(args[3]) + url_oneway.format(0) \
            if len(args) == 4 else url.format(args[0], args[1], args[2]) + url_oneway.format(1)

    @staticmethod
    def create_data():
        """ Create DATA"""
        global DATA
        if len(sys.argv) >= 4:
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


class Line(Page):
    """ Line class """

    def __init__(self, way="outbound"):
        self.lines = []
        j = 1
        while True:
            flag = False
            for i in range(5, 9):
                line = Page.parse_html('string(//div[@class="{0} block"]//table/tbody/tr[{1}]/td[{2}]/label/div/span/@title)'.format(way, 2*j - 1, i))
                self.lines.append(line)
            j += 1
            last = len(self.lines) - 1
            if last > 2:
                if self.lines[last] == '' and self.lines[last - 1] == '' and self.lines[last - 2] == '' and self.lines[last - 3] == '':
                    break



class Flight:
    """ Flight class"""
    def __init__(self, line):
        """ Initialization """
        self.departure = re.search(r'\d\d:\d\d\W\d\d:\d\d', line).group()
        # self.destination = re.search(r'(?<=–)\d\d:\d\d', line).group()
        self.duration = re.search(r'\d\d h \d\d min', line).group()
        """self.departure = self.get_departure()
        self.destination = self.get_destination()
        self.duration = self.get_duration()
        self.class_ = self.get_class()
        self.min_price = self.get_min()
        self.max_price = self.get_max()"""

    def show_flight(self):
        """ Show flight in cmd """
        text = '{0}-{1} {2} {3}-{4} RUB {5}'
        print(text.format(self.departure, self.destination,
                          self.duration, self.min_price,
                          self.max_price, self.class_))


if __name__ == "__main__":
    """parser = argparse.ArgumentParser(description="Read Flight.")
    parser.add_argument()"""
    Page.create_data()
    Page.construct_url()
    Page.get_page()
    Page.get_html()
    """
    line = Line()
    fly = Flight(line.line)"""
    print('\n'.join([x for x in Line().lines if x != '']))
    print('\n'.join([x for x in Line(way="return").lines if x != '']))
