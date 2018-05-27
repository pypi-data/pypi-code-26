# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


class GoogleSearchKeyword(object):

    def __init__(self):
        self.default_looking_search_page = 2

    def get_keywords(self, parse_str):
        keywords = {}
        for page in range(0, self.default_looking_search_page):
            soup = self._search_and_get_soup(parse_str, page)
            results = [x.text for x in soup.find(name="div", id="search").find_all("b")]
            for result in results:
                if result not in keywords:
                    keywords[result] = 1
                else:
                    keywords[result] += 1
        return keywords

    def get_stock_num(self, stock_chinese_name):
        search_str = "{}股票".format(stock_chinese_name)
        soup = self._search_and_get_soup(search_str, 0)

        results = [x.text for x in soup.find(name="div", id="search").find_all("b")]
        for result in results:
            if len(result) == 4 and result.isdigit():
                return result
        raise ValueError("Unable to find stock number for '{}' stock name. Result in '{}'".format(stock_chinese_name, results))

    def _search_and_get_soup(self, search_str, page_count):
        session = requests.session()
        page_par = page_count * 10
        search_url = "https://www.google.com.tw/search?q={0}&oq={0}&aqs=chrome..69i57j69i60l5.2439j0j7&sourceid=chrome&ie=UTF-8&start={1}".format(search_str, page_par)
        response = session.get(search_url).text

        return BeautifulSoup(response, 'html.parser')


if __name__ == '__main__':
    # for k, v in GoogleSearchKeyword().get_keywords("[新聞] 鴻海減資逾兩成，股東哭哭").iteritems():
    #     print "Word : '{}' count : '{}'".format(k.encode("utf-8"), v)

    print str(GoogleSearchKeyword().get_stock_num("鴻海"))
