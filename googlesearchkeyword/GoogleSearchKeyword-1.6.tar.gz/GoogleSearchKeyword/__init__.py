# -*- coding: utf-8 -*-
from xgoogle.search import GoogleSearch
import time
import random
import re


DEFAULT_SEARCH_AMOUNT = 30


class GoogleSearchKeyword(GoogleSearch):

    def get_keywords(self):
        keywords = {}
        self.results_per_page = DEFAULT_SEARCH_AMOUNT
        soup = self._search_and_get_soup()
        results = []
        for title in soup.find("div", {"id": "search"}).findAll("h3"):
            results += ["".join(x.findAll(text=True)).strip() for x in title.findAll("b")]
        for result in results:
            if result not in keywords:
                keywords[result] = 1
            else:
                keywords[result] += 1
        return keywords

    def get_stock_num(self):
        self.query = "{}股票".format(self.query)
        self.results_per_page = 10
        soup = self._search_and_get_soup()
        for title in soup.find("div", {"id": "search"}).findAll("h3"):
            title_a = title.find("a")

            url = title_a['href']
            match = re.match(r'/url\?q=(https://tw.stock.yahoo.com[^&]+)&', url)
            if match:
                m = re.findall('\d+', "".join(title_a.findAll(text=True)).strip())
                if m:
                    for num in set(m):
                        if len(num) == 4 and num.isdigit():
                            return num
        return None

    def _search_and_get_soup(self):
        self.page = 0
        soup = self._get_results_page()
        time.sleep(random.randint(3, 5))  # Try not to annnoy Google, with a random short wait
        return soup


if __name__ == '__main__':
    for k, v in GoogleSearchKeyword("[新聞] 鴻海減資逾兩成，股東哭哭").get_keywords().iteritems():
        print "Word : '{}' count : '{}'".format(k.encode("utf-8"), v)

    print str(GoogleSearchKeyword("鴻海").get_stock_num())
    print str(GoogleSearchKeyword("中鋼").get_stock_num())
    print str(GoogleSearchKeyword("宏達電").get_stock_num())
    print str(GoogleSearchKeyword("緯創").get_stock_num())
