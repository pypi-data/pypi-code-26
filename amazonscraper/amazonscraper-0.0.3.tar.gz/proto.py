# -*- coding: utf-8 -*-
"""
Prototype of the amazon scraper
"""

import requests
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import json

_BASE_URL = "https://www.amazon.com/"
_DEFAULT_BEAUTIFULSOUP_PARSER = "html.parser"
PRODUCT_CSS_SELECTOR = "#resultItems > li"
TITLE_CSS_SELECTOR = "a > div > div.sx-table-detail > h5 > span"
RATING_CSS_SELECTOR = "a > div > div.sx-table-detail > \
    div.a-icon-row.a-size-small > i > span"
CUSTOMER_REVIEW_NB_CSS_SELECTOR = "a > div > \
    div.sx-table-detail > div.a-icon-row.a-size-small > span"
URL_CSS_SELECTOR = "a['href']"
NEXT_PAGE_URL_CSS_SELECTOR = "ul.a-pagination > li.a-last > a['href']"


class Products(object):
    """Class of the products"""
    def __init__(self):
        self.products = []

    def _add_product(self, product_dict):
        self.products.append(product_dict)

    def __repr__(self):
        return json.dumps(self.products, indent=1)

    def __len__(self):
        return len(self.products)

    def __getitem__(self, key):
        """ Method to access the object as a list
        (ex : products[1]) """
        return self.products[key]

    def csv(self, separator=","):
        csv_string = separator.join([
                                    "Product title",
                                    "Rating",
                                    "Number of customer reviews",
                                    "Product URL"])
        for product in self:
            rating = product.get("rating", "")
            if separator == ";":  # French convention
                rating = rating.replace(".", ",")
            csv_string += ("\n"+separator.join([
                                        product.get("title", ""),
                                        rating,
                                        product.get("review_nb", ""),
                                        product.get("url", "")]))
        return csv_string


class Client(object):
    """Do the requests with the Amazon servers"""

    def __init__(self, keywords="", search_url=False):
        """ Init of the client """
        if search_url:
            self.base_url = "https://" + \
                search_url.split("://")[1].split("/")[0] + "/"
            # https://www.amazon.com/s/lkdjsdlkjlk => https://www.amazon.com/
        else:
            self.base_url = _BASE_URL
            search_url = urljoin(
                self.base_url,
                ("s/field-keywords=%s" % (keywords)))

        self.session = requests.session()
        self.headers = {
                    # https://www.amazon.com/lklmk => www.amazon.com
                    'Host': search_url.split("://")[1].split("/")[0],
                    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; \
                        SM-A520F Build/NRD90M; wv) AppleWebKit/537.36 \
                        (KHTML, like Gecko) Version/4.0 \
                        Chrome/65.0.3325.109 Mobile Safari/537.36',
                    'Accept': 'text/html,application/xhtml+xml,\
                        application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    }

        self.products = Products()

        self._get_products(search_url)

    def _get(self, url):
        """ GET request with the proper headers """
        return self.session.get(url, headers=self.headers)

    def _post(self, url, post_data):
        """ POST request with the proper headers """
        return self.session.post(url, headers=self.headers, data=post_data)

    def _get_products(self, product_page_url):
        res = self._get(product_page_url)
        soup = BeautifulSoup(res.text, _DEFAULT_BEAUTIFULSOUP_PARSER)

        # For each product of the result page
        for product in soup.select(PRODUCT_CSS_SELECTOR):
            product_dict = {}
            title = _css_select(product, TITLE_CSS_SELECTOR)
            product_dict['title'] = title
            rating = _css_select(product, RATING_CSS_SELECTOR)
            review_nb = _css_select(product, CUSTOMER_REVIEW_NB_CSS_SELECTOR)
            if rating:
                proper_rating = rating.split(" ")[0].strip()
                product_dict['rating'] = proper_rating
            if review_nb:
                proper_review_nb = review_nb.split("(")[1].split(")")[0]
                product_dict['review_nb'] = proper_review_nb
            url_product_soup = product.select(URL_CSS_SELECTOR)
            if url_product_soup:
                url = urljoin(
                    self.base_url,
                    url_product_soup[0].get('href'))
                proper_url = url.split("/ref=")[0]
                product_dict['url'] = proper_url
                if "slredirect" not in proper_url:  # slredirect = bad url
                    self.products._add_product(product_dict)

        # Check if there is another page
        url_next_page_soup = soup.select(NEXT_PAGE_URL_CSS_SELECTOR)
        if url_next_page_soup:
            url_next_page = urljoin(
                self.base_url,
                url_next_page_soup[0].get('href'))
            self._get_products(url_next_page)
        return


def _css_select(soup, css_selector):
        """ Renvoie le contenu de l'élément du sélecteur CSS, ou une
        chaine vide """
        selection = soup.select(css_selector)
        if len(selection) > 0:
            retour = selection[0].text.strip()
        else:
            retour = False
        return retour

# amazon = Client(keywords = "python+scraping")
amazon = Client(search_url = "https://www.amazon.com/gp/aw/s/ref=is_r_p_n_feature_browse-bin_1?fst=as%3Aoff&rh=n%3A283155%2Ck%3Akubernetes%2Cp_n_feature_browse-bin%3A2656022011&keywords=kubernetes&ie=UTF8&qid=1527897857&rnid=618072011")
# print(amazon.products)  # Prints the dict
print(amazon.products.csv(";"))
# print("%d result(s)" % len(amazon.products))

# TODO : Ajouter une contrainte de nombre max de résultats
# TODO : Mettre en conf
# TODO : Faire le package
# TODO : Faire la CLI
