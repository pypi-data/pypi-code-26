import requests
from bs4 import BeautifulSoup
from datapunt_processing.helpers.files import save_file
from datapunt_processing import logger
import re
from pandas.io.json import json_normalize
from collections import OrderedDict
logger = logger()


def get_pand(lat, lon, radius):
    """
    Get the name the street location where it coordinate resides on.

    Args:
        1. lat: 52.3729378
        2. lon:  4.8937806

    Result:
        Returns dictionary of the pand object
    """

    url = "https://api.data.amsterdam.nl/bag/pand"

    parameters = {"locatie": "{}, {},{}".format(lat, lon, radius),
                  "page_size": 5,
                  "detailed": 1
                  }
    pand_id = None
    response = requests.get(url, params=parameters).json()
    if len(response['results']) > 0:
        pand_id = response['results'][0]['landelijk_id']
    return pand_id


def get_address_near_point(lat, lon, radius):
    """
    Get nearest addres and housenumber based on location.

    ``get_address_near_point(52.3729378, 4.8937806, 50)``

    Args:
        1. lat: 52.3729378
        2. lon:  4.8937806
        3. radius: 50

    Returns:
        Dictionary of the first found address with openbareruimte, huisnummer, postcode, etc...
    """
    lat = str(lat)
    lon = str(lon)
    radius = str(radius)
    results = None
    url_nummeraanduiding = "https://api.data.amsterdam.nl/bag/nummeraanduiding/"
    pand_id = get_pand(lat, lon, radius)

    parameters = {"locatie": "{}, {}, {}".format(lat, lon, radius),
                  # "openbareruimte": openbareruimte["id"],
                  "pand": pand_id,
                  "page_size": 5,
                  "detailed": 1
                  }

    address = requests.get(url_nummeraanduiding, params=parameters).json()
    if len(address["results"]) > 0:
        #print(address["results"][0])
        results = address["results"][0]
    return results


def get_elements(div_content, element_type):
    result = [item.text for item in [row.find_all(element_type) for row in div_content][0]]
    return result


def get_location_information(uri):
    """Get html page, find the header and values by h4 and p and return as a list with 2 values"""
    if isinstance(uri, list):
        uri = uri[0]
    location_page = requests.get(uri).text
    #print(location_page)
    soup = BeautifulSoup(location_page, 'html.parser')
    print(soup.prettify())
    div_content = soup.findAll('div', attrs={"id": "Content"})
    # test = soup.findAll('p')
    location_data = []
    if soup.h4:
        print('true')
        first_key = soup.h4.text
        location_data.append(first_key)
        for sibling in soup.h4.next_siblings:
            for string in sibling:
                location_data.append(repr(string))
        print(location_data)
        #for item in location_data:
        #    re.search(r'<a.*>(.*)<\/a>', item).group(1)
        keys = get_elements(div_content, ['h4'])
        print(keys)
        # html pages are not buildup evenly, so had to hack 2 fields:
        #if keys != []:
        #    if keys[0] != 'Stadsdeel':
        #        keys.insert(0, 'Stadsdeel')
        #    if keys[0] in ('Projectbeschrijving','Bonte Zwaan'):
        #        keys.pop(0)

        #print(headers)
        values = get_elements(div_content, 'p')
        data = dict( zip(keys, values) )
        print(data)
        return data


def get_filename(url):
    url_words = url.split('/')
    print(url_words)
    name = url_words[-1] + '_' + url_words[-2]
    return name


def remove_html_elements(text):
    return re.search(r'<p>(.*)<\/p>', text).group(1)


def add_location_data(location):
    location_data = get_location_information(location['properties']['url'])
    location['properties'].update(location_data)
    lon = location['geometry']['coordinates'][0]
    lat = location['geometry']['coordinates'][1]
    radius = 50
    bag_nummeraanduiding = get_address_near_point(lat, lon, radius)
    if bag_nummeraanduiding:
        location['properties']['bag_adres'] = bag_nummeraanduiding['_display']
        location['properties']['bag_id'] = bag_nummeraanduiding['nummeraanduidingidentificatie']
        location['properties']['bag_verblijfsobject'] = bag_nummeraanduiding['verblijfsobject']
    location['properties']['lat'] = lat
    location['properties']['lon'] = lon
    return location


def cleanup_properties(location):
    if isinstance(location['properties']['url'], list):
        location['properties']['url'] = location['properties']['url'][0]
    if 'summary' in location['properties'].keys():
        location['properties']['summary'] = remove_html_elements(location['properties']['summary'])
    return location


def main():
    urls = [
      'https://www.amsterdam.nl/kunst-cultuur/ateliers/broedplaatsoverzicht',
      'https://www.amsterdam.nl/kunst-cultuur/ateliers/broedplaatsoverzicht/vrijplaatsen-0'
      ]
    params = {
        'zoeken': 'true',
        'geojson': 'true',
        'pager_rows': '500'
    }
    for url in urls:
        response = requests.get(url, params=params).json()
        print(response)
        for location in response["features"]:
            location = cleanup_properties(location)
            location = add_location_data(location)
        filename = get_filename(url)
        logger.info('Saving {}'.format(filename))
        save_file(response, 'data', filename + '.geojson')

        data = []
        for item in response['features']:
            data.append(item['properties'])
        df = json_normalize(data)
        df.to_csv('data/' + filename + '.csv')

if __name__ == '__main__':
    main()
