import requests
from BA.tools import reg_sandwich, is_date, ba_parser, ba_base

class User:
    """Stores and retrieves data from Beer Advocate for a particular user

    Attributes
    ----------
        username : str
            The user's username
        user_id : str
            The user's user_id if the user's profile page is publice
        url : str
            The full URL to the beer's profile page
        reviews : str
            Contains first page of user's reviews 
        info : dict
            Dictionary containing user's info if profile page is public
    """
    def __init__(self, username): 
        self.username = username
        self.user_id = '' 
        first_review_page = ba_base + '/user/beers/?ba=' + username
        
        self.reviews = self._get_pagereviews(first_review_page, first_call = True)
        self.info = self._get_info()

    def _get_info(self):
        """"Returns user info if user has a profile page"""

        parser = ba_parser(attributes = ['class'], vals = ['mainProfileColumn', 'secondaryContent pairsJustified'])
        
        page_html = requests.get(self.url).text
        parser.feed(page_html)
        parser.clean_lines()
        user_dat = parser.lines
        
        user_info = dict()
        index = 0
        while index in range(len(user_dat)):
            if user_dat[index] == 'Likes Received:':
                user_info.update({'Likes Received': user_dat[index + 1]})
                self.username = user_dat[index + 2]
                break
            elif user_dat[index] == ':':
                key = user_dat[index - 1]
                val = user_dat[index + 1]
                user_info.update({key: val})
            elif ':' in user_dat[index]:
                key = user_dat[index][:-1]
                val = user_dat[index + 1]
                user_info.update({key: val})
            index += 1
        if user_info == {}:
            self.private = True
            return 'Sorry, either this user is private or does not exist'
        self.private = False
        return user_info
    
    def _get_pagereviews(self, url, first_call = False):
        """
        Returns all reviews on page
        """
        parser = ba_parser(tags = ['div'],vals = ['ba-content'], 
                            save_comments = True, save_urls = True)
        page_html = requests.get(url).text
        parser.feed(page_html)
        parser.clean_lines()
        review_dat = parser.lines
        
        index = 0
        reviews=[]

        while index in range(len(review_dat)):
            if is_date(review_dat[index], hyphened = True):
                if '%' in review_dat[index + 6]:
                    reviews.append(review_dat[index:index + 7])
                    index+=7
            else:
                index += 1
            
        if first_call:
            self.last_page = 0
            for url in parser.urls:
                if 'start=' in url:
                    page_num = int(reg_sandwich('start=', '&', url))
                    if page_num > self.last_page:
                        self.last_page = page_num
            for comment in parser.comments:
                if 'user_id' in comment:
                    self.user_id = reg_sandwich('id=', '&', comment)
                    break
            self.url = ba_base + '/community/members/'+ self.username + '.' \
                    + self.user_id            
        return reviews  
        
    def get_reviews(self, n_most_recent = 0):
        """Gets reviews by users

        Parameters
        ----------
        If n_most_recent is 0 (default), all reviews are returned. Otherwise, n_most recent is rounded up to the nearest 50th and the result is the number of ratings that are returned, or the total number (whichever is smaller)
            

        Returns
        -------
        list
            The result is a list of slists, where each element is a review by the User
        """
        parser = ba_parser(vals = ['rating_fullview'])
        n_most_recent = self.last_page if n_most_recent == 0 else ((n_most_recent - 1)//50)*50
        all_reviews = self.reviews[:]
        for page_num in range(50,n_most_recent + 1, 50):
            url = ba_base + '/user/beers/?start=' + str(page_num)\
                + '&ba=' + self.username + '&order=dateD&view=R' 
            all_reviews += self._get_pagereviews(url) 
        return all_reviews



