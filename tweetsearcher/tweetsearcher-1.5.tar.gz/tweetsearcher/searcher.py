from tweetsearcher.tweet import Tweet
from urllib import parse
from requests import session
from bs4 import BeautifulSoup
from datetime import datetime
from time import sleep
from random import randint
from os import path
import pandas as pd

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

    def __init__(self, sess=session(), proxy='', headers=default_headers, delay_min=0, delay_max=2, debug=False):
        self.__session = sess
        self.__session.proxies = {}
        if proxy:
            self.__session.proxies['http'] = proxy
            self.__session.proxies['https'] = proxy
        self.headers = headers
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.debug = debug

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

                self.log('%d tweets downloaded' % (len(items_html)))

                for html in items_html:
                    try:
                        tweet = Tweet.fromHtml(str(html))
                        tweets.append(tweet)
                    except:
                        self.log('parse error of some tweet')

                cursor = next_cursor

                if len(items_html) == 0 or 0 < max_tweets <= len(tweets):
                    break
            except Exception as err:
                self.log(err)

            wait_time = randint(self.delay_min, self.delay_max)
            self.log('Waiting %d seconds before downloading the next page' % wait_time)
            sleep(wait_time)

        return tweets, cursor

    def tweets_to_csv(self, q, since='', until='', f='tweets', max_tweets=0, username='', lang='', cursor='',
                      file_name=''):
        if not file_name:
            file_name = 'tweets_%s_%s-%s.csv' % (q, since, until)

        self.log('Downloading tweets started...')
        self.log('All data will be saved to the file named %s' % file_name)

        total_tweets = []
        while True:
            try:
                tweets, next_cursor = self.get_tweets(q, since, until, f, 100, username, lang, cursor)

                if len(tweets) > 0:
                    columns = tweets[0].__dict__.keys()
                    df = pd.DataFrame(columns=columns) if not path.exists(file_name) else pd.read_csv(file_name)
                    total_tweets.extend(tweets)
                    new_tweets_df = pd.DataFrame(
                        [[getattr(i, str(j).strip()) for j in columns] for i in tweets],
                        columns=columns,
                    )
                    df = df.append(new_tweets_df, sort=False)
                    df.to_csv(file_name, index=False)

                # if not path.exists(file_name):
                #     with open(file_name, 'a', encoding='utf-8') as f:
                #         f.write(';'.join(tweets[0].__dict__.keys()))
                #
                # with open(file_name, 'a', encoding='utf-8') as file:
                #     for t in tweets:
                #         total_tweets.append(t)
                #         file.write('\n')
                #         file.write(';'.join(str(v) for v in t.__dict__.values()))

                cursor = next_cursor

                last_datetime = total_tweets[len(total_tweets) - 1].datetime
                self.log('Last downloaded tweet datetime is %s' % last_datetime)
                self.log('Total tweets count: %d' % len(total_tweets))

                if len(tweets) == 0 or 0 < max_tweets <= len(total_tweets):
                    break

            except Exception as err:
                self.log(err)

        self.log('Download successfully completed!')
        self.log('%d tweets saved to the file named %s' % (len(total_tweets), file_name))
        return total_tweets, cursor

    def log(self, *args):
        if self.debug:
            print(args)
