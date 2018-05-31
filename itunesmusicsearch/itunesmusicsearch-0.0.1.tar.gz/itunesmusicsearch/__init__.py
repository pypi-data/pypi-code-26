#!/usr/bin/python
import requests
from itunesmusicsearch import result_item
from itunesmusicsearch import track

name = "itunesmusicsearch"

base_url = 'https://itunes.apple.com/search?term='
ampersand = '&'
parameters = {
    'term': 'term=',
    'country': 'country=',
    'media': 'media=',
    'entity': 'entity=',
    'attribute': 'attribute=',
    'limit': 'limit=',
    'id': 'id=',
    'amgArtistId': 'amgArtistId=',
    'upc': 'upc='
}
entities = {
    'movieArtist': 'movieArtist',
    'movie': 'movie',
    'podcastAuthor': 'podcastAuthor',
    'podcast': 'podcast',
    'musicArtist': 'musicArtist',
    'musicTrack': 'musicTrack',
    'album': 'album',
    'musicVideo': 'musicVideo',
    'mix': 'mix',
    'song': 'song',
    'audiobookAuthor': 'audiobookAuthor',
    'audiobook': 'audiobook',
    'shortFilmArtist': 'shortFilmArtist',
    'shortFilm': 'shortFilm',
    'tvEpisode': 'tvEpisode',
    'tvSeason': 'tvSeason',
    'software': 'software',
    'iPadSoftware': 'iPadSoftware',
    'macSoftware': 'macSoftware',
    'ebook': 'ebook',
    'ebookAuthor': 'ebookAuthor',
    'all': 'all',
    'allArtist': 'allArtist',
    'allTrack': 'allTrack'
}

def search(term, country='UA', media='music', entity=None, attribute=None, limit=50):
    """
    Returns the result of the search of the specified term in an array of result_item(s)
    :param term: String. The URL-encoded text string you want to search for. Example: Steven Wilson.
                 The method will take care of spaces so you don't have to.
    :param country: String. The two-letter country code for the store you want to search.
                    For a full list of the codes: http://en.wikipedia.org/wiki/%20ISO_3166-1_alpha-2
    :param media: String. The media type you want to search for. Example: music
    :param entity: String. The type of results you want returned, relative to the specified media type. Example: musicArtist.
                   Full list: musicArtist, musicTrack, album, musicVideo, mix, song
    :param attribute: String. The attribute you want to search for in the stores, relative to the specified media type.
    :param limit: Integer. The number of search results you want the iTunes Store to return.
    :return: An array of result_item(s)
    """
    search_url = _url_search_builder(term, country, media, entity, attribute, limit)
    r = requests.get(search_url)

    try:
        json = r.json()['results']
        result_count = r.json()['resultCount']
    except:
        raise ConnectionError('Cannot fetch JSON data')

    if result_count == 0:
        raise LookupError('No results found' + str(term))

    return _get_result_list(json)


def _url_search_builder(term, country='UA', media='music', entity=None, attribute=None, limit=50):
    """
    Builds the URL to perform the search based on the provided data
    :param term: String. The URL-encoded text string you want to search for. Example: Steven Wilson.
                 The method will take care of spaces so you don't have to.
    :param country: String. The two-letter country code for the store you want to search.
                    For a full list of the codes: http://en.wikipedia.org/wiki/%20ISO_3166-1_alpha-2
    :param media: String. The media type you want to search for. Example: music
    :param entity: String. The type of results you want returned, relative to the specified media type. Example: musicArtist.
                   Full list: musicArtist, musicTrack, album, musicVideo, mix, song
    :param attribute: String. The attribute you want to search for in the stores, relative to the specified media type.
    :param limit: Integer. The number of search results you want the iTunes Store to return.
    :return: The built URL as a string
    """
    built_url = base_url + _parse_query(term)
    built_url += ampersand + parameters['country'] + country
    built_url += ampersand + parameters['media'] + media

    if entity is not None:
        built_url += ampersand + parameters['entity'] + entity

    if attribute is not None:
        built_url += ampersand + parameters['attribute'] + attribute

    built_url += ampersand + parameters['limit'] + str(limit)

    return built_url


def _parse_query(query):
    """
    Replaces every space in the provided query with a +
    :param query: term to delete spaces
    :return: query without spaces as a string
    """
    return str(query).replace(' ', '+')


def _get_result_list(json):
    """
    Analyzes the provided JSON data and returns an array of result_item(s) based on its content
    :param json: Raw JSON data to analyze
    :return: An array of result_item(s) from the provided JSON data
    """
    result_dict = []

    for item in json:
        if 'wrapperType' in item:
            # Music
            if item['wrapperType'] == 'track' and item['kind'] == 'song':
                music_track_result = track.Track(item)
                result_dict.append(music_track_result)
        else:
            unknown_result = result_item.ResultItem(item)
            result_dict.append(unknown_result)

    return result_dict


def search_track(term, country='UA', attribute=None, limit=1):
    return search(term, country, 'music', entities['song'], attribute, limit)
