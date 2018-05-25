from datetime import datetime
from bs4 import BeautifulSoup
import re


class Tweet:

    def __init__(self, id=0, text='', datetime=datetime.now(), link='', retweets=0, favorites=0,
                 username='', user_id=0, user_link=''):
        self.id = id
        self.datetime = datetime
        self.text = text
        self.link = link
        self.retweets = retweets
        self.favorites = favorites
        self.username = username
        self.user_id = user_id
        self.user_link = user_link

    def __str__(self):
        return str(self.__dict__)

    def get_mentions(self):
        return re.compile('(@\\w*)').findall(self.text)

    def get_hashtags(self):
        return re.compile('(#\\w*)').findall(self.text)

    @staticmethod
    def fromHtml(html):
        soup = BeautifulSoup(html, 'lxml')
        tweet = soup.find('div', {'class': 'tweet'})
        tweet_content = tweet.find('div', {'class': 'content'})
        tweet_header = tweet_content.find('div', {'class': 'stream-item-header'})
        tweet_footer = tweet_content.find('div', {'class': 'stream-item-footer'})
        tweet_text = tweet_content.find('div', {'class': 'js-tweet-text-container'})
        timestamp = int(tweet_header.find('small', {'class': 'time'}) \
                        .find('span', {'class': '_timestamp'}) \
                        .get('data-time'))
        text = re.sub(r"\s+", " ", tweet_text.text)
        retweets = int(tweet_footer.find('span', {'class': 'ProfileTweet-action--retweet'}) \
                       .find('span', {'class': 'ProfileTweet-actionCount'}) \
                       .get('data-tweet-stat-count'))
        favorites = int(tweet_footer.find('span', {'class': 'ProfileTweet-action--favorite'}) \
                        .find('span', {'class': 'ProfileTweet-actionCount'}) \
                        .get('data-tweet-stat-count'))
        return Tweet(id=int(tweet.get('data-tweet-id')),
                     datetime=datetime.fromtimestamp(timestamp),
                     text=text,
                     link=tweet.get('data-permalink-path'),
                     retweets=retweets,
                     favorites=favorites,
                     username=tweet.get('data-name'),
                     user_id=int(tweet_header.find('a').get('data-user-id')),
                     user_link=tweet_header.find('a').get('href'))
