#!/usr/bin/python
import json
import requests

from lxml import html


USER_AGENT = "Mozilla/5.0 (Windows NT 12.0; WOW64) AppleWebKit/" + \
    "537.46 (KHTML, like Gecko) Chrome/47.0.2454.88 Safari/537.46"
HEADERS = {"User-Agent": USER_AGENT}


# From https://www.niaaa.nih.gov/alcohol-health/overview-alcohol-consumption/moderate-binge-drinking
# Binge Drinking = 5 or more drinks in a 2 hour window
# Heavy Drinking = 5 or more days of Binge Drinking in a month
class User():
    """User - get user stats"""

    def __init__(self, username):
        self._username = username

    def fetch_user_data(self):
        user_data = dict(
            stats=self._get_user_stats(),
            friends=self._get_user_friends(),
            recent_beers=self._get_user_beers(sort="date"),
            top_rated_beers=self._get_user_beers(sort="highest_rated_their"),
            top_veneus=self._get_user_top_venues()
        )
        return user_data

    def _get_web_page_from_untappd(self, url):
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print("Error from Untappd: {}".format(str(e)))

    def _get_user_stats(self):
        url = "https://untappd.com/user/{}".format(self._username)
        page = self._get_web_page_from_untappd(url)
        return self._parse_user_stats_page(page)

    def _parse_user_stats_page(self, page):
        user_stats = {}
        tree = html.fromstring(page)
        stats_div = tree.find_class("stats")
        for stat in stats_div[0].iterchildren():
            title = stat.find_class("title")[0].text_content()
            value = stat.find_class("stat")[0].text_content()
            user_stats[title] = value
        return user_stats

    def _get_user_friends(self):
        url = "https://untappd.com/user/{}/friends".format(self._username)
        page = self._get_web_page_from_untappd(url)
        return self._parse_user_friends_page(page)

    def _parse_user_friends_page(self, page):
        user_friends = []
        tree = html.fromstring(page)
        friend_items = tree.find_class("friend-item")
        for friend in friend_items:
            user_friends.append(friend.find_class("username")[0].text_content())
        return user_friends

    def _get_user_beers(self, sort="date"):
        url = "https://untappd.com/user/{}/beers?sort={}".format(self._username, sort)
        page = self._get_web_page_from_untappd(url)
        return self._parse_user_beers_page(page)

    def _parse_user_beers_page(self, page):
        user_beers = []
        tree = html.fromstring(page)
        beer_list = tree.find_class("distinct-list-list-container")
        for beer in beer_list[0].iterchildren():
            beer_details = {}
            beer_name_class = beer.find_class('name')
            if(len(beer_name_class) > 0):
                beer_name_link = beer_name_class[0].xpath("./a")
                if(len(beer_name_link) > 0):
                    beer_details['beer_name'] = beer_name_link[0].text_content()
            brewery_name_class = beer.find_class('brewery')
            if(len(brewery_name_class) > 0):
                brewery_name_link = brewery_name_class[0].xpath("./a")
                if(len(brewery_name_link) > 0):
                    beer_details['brewery_name'] = brewery_name_link[0].text_content()
            style_class = beer.find_class('style')
            if(len(style_class) > 0):
                beer_details['style'] = style_class[0].text_content()
            abv_class = beer.find_class('abv')
            if(len(abv_class) > 0):
                beer_details['abv'] = abv_class[0].text_content()
            ibu_class = beer.find_class('ibu')
            if(len(ibu_class) > 0):
                beer_details['ibu'] = ibu_class[0].text_content()
            checkins_class = beer.find_class('check-ins')
            if(len(checkins_class) > 0):
                beer_details['total_check_ins'] = checkins_class[0].text_content()
            checkin_dates = {}
            for checkin_date in beer.find_class('date'):
                checking_type = checkin_date.xpath('./a')[0].get('data-track')
                checking_date = checkin_date.find_class('date-time')[0].text_content()
                checkin_dates[checking_type] = checking_date
            if(len(checkin_dates) > 0):
                beer_details['checkin_dates'] = checkin_dates
            if beer_details != {}:
                user_beers.append(beer_details)
        return user_beers

    def _get_user_top_venues(self):
        url = "https://untappd.com/user/{}/venues?type=&sort=highest_checkin".format(self._username)
        page = self._get_web_page_from_untappd(url)
        return self._parse_user_top_venues(page)

    def _parse_user_top_venues(self, page):
        user_top_veneus = []
        tree = html.fromstring(page)
        venues = tree.find_class("distinct-list-container")[0]
        for venue in venues.iterchildren():
            venue_infos = {}
            venue_name_class = venue.find_class("name")
            if(len(venue_name_class) > 0):
                venue_link = venue_name_class[0].xpath("./a")
                if(len(venue_link) > 0):
                    venue_infos['name'] = venue_link[0].text_content()
            category_class = venue.find_class("category")
            if(len(category_class) > 0):
                venue_infos['category'] = category_class[0].text_content()
            address_class = venue.find_class("address")
            if(len(address_class) > 0):
                venue_infos['address'] = address_class[0].text_content()
            for details in venue.find_class('details'):
                venue_visit_info = {}
                for date_info in details.find_class('date'):
                    date_info_link = date_info.xpath("./a")
                    if(len(date_info_link) > 0):
                        key = date_info_link[0].get('data-href')
                        value = date_info_link[0].text_content()
                        venue_visit_info[key] = value
                check_ins_class = details.find_class('check-ins')
                if(len(check_ins_class) > 0):
                    venue_visit_info['total-visits'] = check_ins_class[0].text_content()
            venue_infos['vist_info'] = venue_visit_info
            user_top_veneus.append(venue_infos)
        return user_top_veneus
