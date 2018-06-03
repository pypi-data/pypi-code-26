import cfscrape
from anime_downloader.sites.anime import BaseAnime, BaseEpisode
from anime_downloader.sites.exceptions import NotFoundError
from anime_downloader.sites import util
from bs4 import BeautifulSoup
import logging
import re

scraper = cfscrape.create_scraper()


class KissanimeEpisode(BaseEpisode):
    QUALITIES = ['360p', '480p', '720p']
    _base_url = 'https://kissanime.ru'
    VERIFY_HUMAN = True

    def getData(self):
        url = self._base_url+self.episode_id
        r = scraper.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')

        if self.VERIFY_HUMAN:
            episode_url = soup.find('form',
                                    {'id': 'formVerify'}).find('a')['href']
        else:
            episode_url = self.episode_id

        print(self._base_url+episode_url)

        ret = scraper.get(self._base_url+episode_url)

        rapid_re = re.compile(r'iframe.*src="https://(.*?)"')
        rapid_url = rapid_re.findall(ret.text)[0]

        data = util.get_stream_url_rapidvideo('https://'+rapid_url,
                                              self.quality)

        self.stream_url = data['stream_url']
        self.title = data['title']
        self.image = data['image']


class Kissanime(BaseAnime):
    sitename = 'kissanime'
    QUALITIES = ['360p', '480p', '720p']
    _episodeClass = KissanimeEpisode

    def getEpisodes(self):
        self._episodeIds = []
        r = scraper.get(self.url)
        soup = BeautifulSoup(r.text, 'html.parser')

        self._getMetadata(soup)

        self._episodeIds = self._getEpisodeUrls(soup)
        self._len = len(self._episodeIds)

        logging.debug('EPISODE IDS: length: {}, ids: {}'.format(
            self._len, self._episodeIds))

        return self._episodeIds

    def _getEpisodeUrls(self, soup):
        ret = soup.find('table', {'class': 'listing'}).find_all('a')
        ret = [str(a['href']) for a in ret]

        if ret == []:
            err = 'No episodes found in url "{}"'.format(self.url)
            args = [self.url]
            raise NotFoundError(err, *args)

        return list(reversed(ret))
