from tweetsearcher.tweet import Tweet
from urllib import parse
from requests import session
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from random import randint
from os import path

__url = "https://twitter.com/i/search/timeline?f=%s&q=%s&src=typd&%smax_position=%s"


def prepare_data(q, since, until, f, username, lang, cursor):
    urlGetData = ''
    if username:
        urlGetData += ' from:' + username

    if since:
        urlGetData += ' since:' + since

    if until:
        urlGetData += ' until:' + until

    if q:
        urlGetData += ' ' + q

    if lang:
        urlLang = 'lang=' + lang + '&'
    else:
        urlLang = ''
    return __url % (f, parse.quote(urlGetData), urlLang, cursor)


default_headers = {
    'Host': "twitter.com",
    'User-Agent': 'Chrome/66.0.3359.181',
    'Accept': "application/json, text/javascript, */*; q=0.01",
    'Accept-Language': "de,en-US;q=0.7,en;q=0.3",
    'X-Requested-With': "XMLHttpRequest",
    'Connection': "keep-alive"
}


class TweetSearcher():

    def __init__(self, sess=session(), proxy='', headers=default_headers, delay_min=0, delay_max=2):
        self.__session = sess
        self.__session.proxies = {}
        if proxy:
            self.__session.proxies['http'] = proxy
            self.__session.proxies['https'] = proxy
        self.headers = headers
        self.delay_min = delay_min
        self.delay_max = delay_max

    def get_tweets_json(self, q, since='', until='', f='tweets', username='', lang='', cursor='', session=None):
        url = prepare_data(q, since, until, f, username, lang, cursor)
        self.headers['Referer'] = url
        return session.get(url, headers=self.headers).json()

    def get_tweets(self, q, since='', until='', f='tweets', max_tweets=0, username='', lang='', cursor=''):
        tweets = []

        while True:
            try:
                response_json = self.get_tweets_json(q, since, until, f, username, lang, cursor, self.__session)
                next_cursor = response_json['min_position']
                soup = BeautifulSoup(response_json['items_html'], 'lxml')
                items_html = soup.find_all('div', {'class': 'tweet'})

                print('%d tweets downloaded' % (len(items_html)))

                for html in items_html:
                    try:
                        tweet = Tweet.fromHtml(str(html))
                        tweets.append(tweet)
                    except:
                        print('parse error of some tweet')

                cursor = next_cursor

                if len(items_html) == 0 or 0 < max_tweets <= len(tweets):
                    break
            except Exception as err:
                print(err)

            wait_time = randint(self.delay_min, self.delay_max)
            print('Waiting %d seconds before downloading the next page' % wait_time)
            sleep(wait_time)

        return tweets, cursor

    def tweets_to_csv(self, q, since='', until='', f='tweets', max_tweets=0, username='', lang='', cursor='',
                      file_name=''):
        if not file_name:
            file_name = 'tweets_%s_%s.csv' % (q, datetime.now())

        print('Downloading tweets started...')
        print('All data will be saved to the file named %s' % file_name)

        total_tweets = []
        while True:
            try:
                tweets, next_cursor = self.get_tweets(q, since, until, f, 100, username, lang, cursor)
                if not path.exists(file_name): open(file_name, 'a').write(';'.join(tweets[0].__dict__.keys()))
                with open(file_name, 'a') as file:
                    for t in tweets:
                        total_tweets.append(t)
                        file.write('\n')
                        file.write(';'.join(str(v) for v in t.__dict__.values()))
                cursor = next_cursor

                last_datetime = total_tweets[len(total_tweets) - 1].datetime
                print('Last downloaded tweet datetime is %s' % last_datetime)
                print('Total tweets count: %d' % len(total_tweets))

                if len(tweets) == 0 or 0 < max_tweets <= len(total_tweets):
                    break

            except Exception as err:
                print(err)

        print('Download successfully completed!')
        print('%d tweets saved to the file named %s' % (len(total_tweets), file_name))
        return total_tweets, cursor
