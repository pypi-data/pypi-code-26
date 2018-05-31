import requests

class SimpleFrameworkSession():
    
    def __init__(self, base_url, view = False):
        self.BASE_URL = base_url
        if self.BASE_URL[-1] != '/':
            self.BASE_URL += '/'
        

        self.default_view = view
        self.is_session_authenticated = False
        
        self._session = None

    
    def _set_session_headers(self, auth_token, cache_control = None):
#         authtoken = response.json()['data'][0]['token'] # it MUST always be this format.

        headers = { 
                    'Accept': 'application/json' ,
                    'Content-Type' : 'application/json',
                    'AUTHORIZATION' : 'Token {token}'.format(token = auth_token)
        }
        
        if cache_control in ['no-cache']:
            headers['Cache-Control'] = cache_control
        
        self.session.headers = headers
    
    @property
    def session(self):
        if self._session == None:
            self._session = requests.Session()
            
        return self._session
    
    def url_formatter(self, url, base_url = None):
        if url.find('http')>=0:
            full_url = url
        else:
            
            if url[0] == '/':
                url = url[1:]
            
            
            if base_url == None:
            
                full_url = self.BASE_URL + url
            else:
                
                if base_url[-1] != '/':
                    base_url += '/'
                
                full_url = base_url + url
            
        appender =None
        if url.find('format')>=0:
            pass
        elif url.find('?') >=0:
            appender = '&'
        else:
            appender = '?'

        if appender:
            full_url = full_url + appender + 'format=json'
        

        return full_url

    def send_query(self, method_type, url, view = None, **kwargs):
        
        response = self.session.request(method_type, url = self.url_formatter(url), **kwargs)

        if (view == None and self.default_view) or view == True:
            self.view(response = response)
        return response
    
    def view(self, response):
        
        try:
            print(response.json())
        except:
            print(response.content)

    def get(self, url, **kwargs):
        return self.send_query(method_type = 'get', url = url, **kwargs)

    def post(self, url, **kwargs):
        return self.send_query(method_type = 'post', url = url,  **kwargs)

    def put(self, url, **kwargs):
        return self.send_query(method_type = 'put', url = url,  **kwargs)

    def delete(self, url, **kwargs):
        return self.send_query(method_type = 'delete', url = url,  **kwargs)

if __name__ == '__main__':
    
    
    rs = SimpleFrameworkSession(base_url = 'http://localhost:8000/')
    
    
    password = {'username' : 'test12', 'password' : 'test12'}
    response = rs.login(username = 'test12', password = 'test12', override_id = 3)
    
    response = rs.get('profile/models/')
    
    print(response.json())
    