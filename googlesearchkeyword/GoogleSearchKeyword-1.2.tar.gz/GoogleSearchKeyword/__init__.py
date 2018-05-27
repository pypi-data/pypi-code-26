# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


class GoogleSearchKeyword(object):

    def __init__(self):
        self.default_looking_search_page = 2

    def get_keywords(self, parse_str):
        keywords = {}
        for page in range(0, self.default_looking_search_page):
            results = self.search(parse_str, page)
            for result in results:
                if result not in keywords:
                    keywords[result] = 1
                else:
                    keywords[result] += 1
        return keywords

    def search(self, search_str, page_count):
        session = requests.session()
        page_par =page_count * 10
        search_url = "https://www.google.com.tw/search?q={0}&oq={0}&aqs=chrome..69i57j69i60l5.2439j0j7&sourceid=chrome&ie=UTF-8&start={1}".format(search_str, page_par)
        response = session.get(search_url).text

        soup = BeautifulSoup(response, 'html.parser')

        return [x.text for x in soup.find(name="div", id="search").find_all("b")]


if __name__ == '__main__':
    for k, v in GoogleSearchKeyword().get_keywords("[新聞] 鴻海減資逾兩成，股東哭哭").iteritems():
        print "Word : '{}' count : '{}'".format(k.encode("utf-8"), v)
