name = 'spaw'

import requests
import json


class SPAW:
    """
    Streamable API require a Streamable account for Basic Auth to use the API.
    Authentication is not need to Retrieve a video in oEmbed format, but the is needed for the rest of functions.

    Args:
        email: Streamable account email 
        password: Streamable account password 

    """

    def __init__(self):
        self.email = None
        self.password = None

    def auth(self, email, password):
        self.email = email
        self.password = password

    def videoUpload(self, file_name):
        """
        Takes given filename and uploads onto Streamable. 

        Args:
            file_name: File name with full path to the file to upload
        
        Returns:
            JSON with Shortcode and Status. {'status': int, 'shortcode': 'url_code'}

        """

        file_processed = {
            'file': (file_name, open(file_name, 'rb')),
        }

        try:
            response = requests.post('https://api.streamable.com/upload', auth=(self.email, self.password), files=file_processed).json()
            return response
        except requests.exceptions.RequestException as e:
            return str(e)

    def videoImport(self, url):
        """
        Takes given URL of a video and imports/uploads it onto Streamable. 

        Args:
            url: URL link for the video to import/upload onto Streamable.
        
        Returns:
            JSON with Shortcode and Status. {'status': int, 'shortcode': 'url_code'}

        """
        try:
            response = requests.get('https://api.streamable.com/import?url='+url, auth=(self.email, self.password)).json()
            return response
        except requests.exceptions.RequestException as e:
            return str(e)

    def retrieve(self, shortcode,  _format='raw'):
        """
        Retrieves a Streamable video as embed code given the shortcode of video URL.
        The embed video can be retrieved as oEmbed or a raw mp4.  
        _format is by default set to 'raw'. 

        Args:
            shortcode: The shortcode can be found at the end of the video URL.
            _format: The format of the retrieved video, either 'oEmbed' or 'raw'.  

        Returns:
            JSON for the embed code for the video.

        e.g. _retrieve('moo', 'raw')
        {"status": 2, "files": {"mp4": {"status": 2, "width": 480, "url": "//cdn-b-west.streamable.com/video/f6441ae0c84311e4af010bc47400a0a4.mp4?token=44kJAXLZqsJ7k3IfwgwlNQ&expires=1528560095", "bitrate": 0, "duration": 0, "size": 0, "framerate": 0, "height": 480}}, "embed_code": "<div style=\"width: 100%; height: 0px; position: relative; padding-bottom: 56.338%;\"><iframe class=\"streamable-embed\" src=\"https://streamable.com/o/moo\" frameborder=\"0\" scrolling=\"no\" style=\"width: 100%; height: 100%; position: absolute;\" allowfullscreen></iframe></div>", "source": null, "thumbnail_url": "//images.streamable.com/west/image/f6441ae0c84311e4af010bc47400a0a4.jpg?height=100", "url": "streamable.com/moo", "message": null, "title": "\"Please don't eat me!\"", "percent": 100}

        e.g. _retrieve('moo', 'oEmbed')
        {"provider_url": "https://streamable.com", "html": "<iframe class=\"streamable-embed\" src=\"https://streamable.com/o/moo\" frameborder=\"0\" scrolling=\"no\" width=\"852\" height=\"480\" allowfullscreen></iframe>", "version": "1.0", "title": "\"Please don't eat me!\"", "type": "video", "provider_name": "Streamable", "thumbnail_url": "//images.streamable.com/west/image/f6441ae0c84311e4af010bc47400a0a4.jpg?height=100", "width": 852, "height": 480}
        
        """

        if _format == 'raw':
            try:
                response = requests.get('https://api.streamable.com/videos/'+str(shortcode), auth=(self.email, self.password)).json()
                return response
            except requests.exceptions.RequestException as e:
                return str(e)
        
        if _format == 'oEmbed':
            try:
                response = requests.get('https://api.streamable.com/oembed.json?url=https://streamable.com/'+str(shortcode)).json()
                return response
            except requests.exceptions.RequestException as e:
                return str(e)