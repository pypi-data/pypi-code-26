from html.parser import HTMLParser
from datetime import datetime
import re

ba_base = 'https://www.beeradvocate.com'

def is_date(string, hyphened = False):
    """
    Tests string to see if it is a date of "%m-%d-%Y" or  "%b %d %Y" format.

    Parameters
    ----------
    string : str
        String to be tested 
    hyphened : bool
        If hyphened is true, tests string for "%m-%d-%Y" format. Otherwise, tests for "%b %d %Y" format   

    Returns
    -------
    bool
        Returns true if string is date of "%m-%d-%Y" or  "%b %d %Y" format, false otherwise.

    """
    if hyphened:
        try:
            datetime.strptime(string, "%m-%d-%Y")
            return True
        except:
            return False
    else:
        try:
            datetime.strptime(string, "%b %d %Y")
            return True
        except:
            return False

def reg_sandwich(look_behind = ' ', look_ahead = ' ', string = ''):
    """Matches a string sandwiched between two other strings using RegEx
    
    If you think of the desired substring as sandwiched between two other strings, the look_behind (left) and look_ahead (right),
    then the desired string is the meat
    

    Parameters
    ----------
    look_behind : str
        The string immediately to the left of the desired substring (bottom bread in the sanwich)
    look_ahead : str
        The string immediately to the right of the desired substring (top bread in the sandwich)
    string : str
        The string to be searched

    Returns
    -------
    str
        Returns the *last* matched group in the paramter string according to the regular expression

    """
    reg_ex = '(?<=' + look_behind +')(.*?)(?=' + look_ahead + ')'
    meat_grabber = re.compile(reg_ex)
    return meat_grabber.search(string).group(0)
class ba_parser(HTMLParser):
    """Although this class may work for general HTML parsing, it was intended for parsing HTML pages on Beer Advocate
    
    After initializing ba_parser(), feed an HTML string as an argument to ba_parser.feed(). Use the ba_parser.clean_lines()
    method to remove the specified characters/strings in the method. The cleaned lines will be stored in ba_parser.lines. 

    Attributes
    ----------
    lines : slist
        List of parsed HTML lines
    comments : slist
        If save_comments = True, comments is a list of all comments parsed when the parser is recording 
    urls: slist
        If save_urls = True, urls is a list of all urls parsed when the parser is recording 

    """
    def __init__(self, tags = ['div'], attributes = ['id'],  vals = ['item_stats','info_box'], 
                 save_comments = False, save_urls = False):
        """Initializes the class

    Parameters
    ----------
    tags : slist
        HTML tags that trigger the parser to start recording
    attributes : slist
        Tags (see above) only trigger the parser to start recording if they contain at least one of the attributes in this list 
    vals : slist
        Tags only trigger the parser to start recording if the value for the attributes (see above) is equal to at least one
        value in vals
    save_comments : bool, optional
        If True, all comments parsed while recording will be stored
    save_urls : bool, optional
        If True, all comments parsed while recording will be stored

    """
        HTMLParser.__init__(self)
        #Parser is recording only if reading > 0
        self.reading = 0
        self.tags = tags
        self.attributes = attributes
        self.vals = vals
        
        self.save_comments = save_comments
        self.save_urls = save_urls
        
        #Attributes to be accessed
        self.lines = []
        if save_comments:
            self.comments = []
        if save_urls:
            self.urls = []
    def handle_starttag(self, tag, attributes):
        """
        Hanldes startags according to how it is specified in the parameters section of the __init__ method
        """
        #Record URLS
        if self.save_urls:
            for attr, value in attributes: 
                if self.reading and attr == 'href':
                    self.urls.append(value)
        #Ignore tags not of interest
        if tag not in self.tags:
            return
        
        #Allows for tags of interest to be nested within tags
        if self.reading:
            self.reading += 1
            return
        
        #Trigger recording
        for attr, value in attributes: 
            if attr in self.attributes and value in self.vals:
                self.reading = 1
                break
               
    def handle_endtag(self, tag):
        """Handles endtags
        The parser is recording lines only if self.reading > 0. If the tag is not nested, this tells the parser to stop
        recording. Otherwise, it helps keep track of the nesting.
        """
        if tag in self.tags and self.reading:
            self.reading -= 1
    
    def handle_data(self, data):
        """
        Stores all lines located between tags when recording
        """
        if self.reading:
            self.lines.append(data)
    def clean_lines(self):
        """Removes unwanted characters from 'lines' attribute
        Removes the folowing substrings from the lines:
        -'\n'
        -'\t'
        -'\xa0'
        -'/'
        -','
        These are common on the Beer Advocate pages
        """
        self.lines = [s.replace('\n','')\
                      .replace('\t','')\
                      .replace('\xa0','')\
                      .replace('/', '')\
                      .replace(',', '')\
                      for s in self.lines]
        self.lines = [s for s in self.lines if s != '' and s!= ' ']
    def handle_comment(self, data):
        """
        If save_comments = True, this function saves all comments parsed while function is recording
        """
        if self.save_comments:
            self.comments.append(data)
            
