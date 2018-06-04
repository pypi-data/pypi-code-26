import requests
from BA.tools import reg_sandwich, is_date, ba_parser, ba_base

def beer_search(beer_name = ' ', first_on_list = True):
    """Searches for beers on Beer Advocate
    
    Sometimes a search will turn up the beer's page if it is an exact match. In this case, the function will return the URL
    corresponding to the search because it can be passed directly into a Beer object.

    Parameters
    ----------
        beer_name : str
            The beer to be searched.
        first_on_list : bool
            If True, the functions return only the URL of the first result on the list

    Returns
    -------
        str
            If either an exact match or first_on_list = True, a string that can be passed in to a Beer object is returned
        dict
            If multiple beers match and first_on_list = False, a dictionary of Beers, corresponding breweries, and 
        corresponding urls are returned
    """
    beer_name = ba_base + '/search/?q=' + beer_name.replace(' ', '+') + '&qt=beer'
    try:
        Beer(beer_name).info
        return beer_name.split(ba_base)[1]
    except:
        parser = ba_parser(vals = ['ba-content'], save_urls = True)
        page_html = requests.get(beer_name).text
        parser.feed(page_html)
        parser.clean_lines()
        
        search_results = parser.lines
        
        index = 0
        beers = []
        breweries = []
        while index in range(len(search_results)):
            if '| ' in search_results[index]:
                beers += search_results[index - 2]
                breweries += search_results[index - 1]
                index += 3
            else:
                index += 1
        try:
            if first_on_list:
                return parser.urls[0]
            
            return {'beer': beers, 'brewery': breweries, 'beer_url': parser.urls[::2], 'brewery_url': parser.urls[1::2]}
        except:
            print('No results. Try being more specific.')
class Beer:
    """Stores and retrieves data from Beer Advocate for a particular beer

    Attributes
    ----------
        url : str
            The full URL to the beer's profile page
        main_html : str
            HTML for beer's profile page
        info : dict
            Dictionary of beer info and stats from the beer's profile page
        last_page : int
            The page number corresponding to the last page. Used for getting all reviews

    """
    def __init__(self, url):
        """Initializes the class
        
    Parameters
    ----------
    url : str
        The part of the beer's url *after* http://beeradvocate.com
    param2 : :obj:`str`, optional
        The second parameter.
    *args
        Variable length argument list.
    **kwargs
        Arbitrary keyword arguments.

    Returns
    -------
    None
    """
        self.url = ba_base + url
        self.main_html = requests.get(self.url).text
        self.info = self.get_info()
        self.last_page = int(self.info['Ratings'][0]) - (int(self.info['Ratings'][0]) % 25)
    def get_info(self):
        """"Returns beer info and stats from the beer's profile page"""
        parser = ba_parser()
        parser.feed(self.main_html)
        parser.clean_lines()
        info = parser.lines
        beer_info = dict()
        index = 0
        first = True
        while index in range(len(info)):
            if info[index] == ':':
                key = info[index - 1]
                val = info[index + 1]
                beer_info.update({key: [val]})
                index+=2
            elif ':' in info[index]:
                if not first:
                    vals = info[key_index + 1:index]
                    beer_info.update({key: vals})
                    key = info[index][:-1]
                    key_index = index
            
                else:
                    first = False
                    key = info[index][:-1]
                    key_index = index
            index+=1
        return beer_info        
    
    def get_name(self):
        """Returns the beer's name"""
        return reg_sandwich('<title>', '<', self.main_html).split(' |')[0]
    
    def get_reviews(self, n_most_recent = 0):
        """Gets beer's reviews

        Parameters
        ----------
        If n_most_recent is 0 (default), all reviews are returned. Otherwise, n_most recent is rounded up to the nearest 25th and the result is the number of ratings that are returned, or the total number (whichever is smaller)
            

        Returns
        -------
        dict
            Dictionary of all usernames and corresponding beer review

        """
        parser = ba_parser(vals = ['rating_fullview'])
        n_most_recent = ((n_most_recent - 1)//25)*25 if n_most_recent != 0 else self.last_page
        names = []
        reviews = []
        for page_num in range(0,n_most_recent + 1, 25):
            all_review_dat = self._get_pagereviews(self.url + '?view=beer&sort=&start=' + str(page_num)) 
            names+= all_review_dat[0] 
            reviews += all_review_dat[1]
        all_reviews = {'usr': names, 'review': reviews}
        return all_reviews
    def _get_pagereviews(self, url):
        """Gets all reviews on the page

        Parameters
        ----------
        url
            The url of the Beer Advocate beer page 
        Returns
        -------
        tuple
            List of users and corresponding usernames and ratings
        """
        parser = ba_parser(vals = ['rating_fullview'])
        page_html = requests.get(url).text
        parser.feed(page_html)
        parser.clean_lines()
        review_dat = parser.lines

        index = 0
        last_index = 0
        users=[]
        reviews=[]
        while index in range(len(review_dat)):
            if is_date(review_dat[index]):
                users.append(review_dat[index - 1])
                reviews.append(review_dat[last_index:index - 1])
                last_index = index + 1       
            index += 1
        return (users, reviews)
