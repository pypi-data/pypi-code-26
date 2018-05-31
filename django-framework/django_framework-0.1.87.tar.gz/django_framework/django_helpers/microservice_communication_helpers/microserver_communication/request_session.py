import requests
from simple_request_session import SimpleFrameworkSession

class FrameworkSession(SimpleFrameworkSession):
    
#     def __init__(self, base_url, view = False):
#         self.BASE_URL = base_url
#         if self.BASE_URL[-1] != '/':
#             self.BASE_URL += '/'
#         
# 
#         self.default_view = view
#         self.is_session_authenticated = False
#         
#         self._session = None
    
    def login(self, username, password, override_username = None, override_uuid = None, override_id = None):
        self._login(username = username, password = password, override_username = override_username, override_uuid = override_uuid)
        
        if override_id:
            self._login_via_override_id(username, password, override_id = override_id)
        
    def _login_via_override_id(self, username, password, override_id):
        
        profile_uuid = None
        if override_id: # *sigh fine.
            response = self.send_query(method_type = 'GET', url = '/admin/profile/models/?filter[id]={profile_id}'.format(profile_id = override_id), view = False)
            response = response.json()
            
            if len(response['data']) > 0: # and there really shoudl only be one
                profile_uuid = response['data'][0]['uuid']
        
        if not profile_uuid:
            raise ValueError('The profile_id was not found! Check the ID or the login credentials (make sure its admin)')

        return self._login(username = username, password = password, override_uuid = profile_uuid)

    def _login(self, username, password, override_username = None, override_uuid = None):
        login_payload = dict(
            username = username,
            password = password)
        
        if override_username:
            login_payload['override'] = override_username

        elif override_uuid:
            login_payload['override_uuid'] = override_uuid
        
        
        response = self.send_query(method_type = 'POST', url = '/login/', json = login_payload, view = False)
        if response.status_code > 400:
            raise ValueError('Unable to login with the provided credentials for admin.  Or the override information provided was not valid (user not found)')
        
        auth_token = response.json()['data'][0]['token']
        self._set_session_headers(authtoken = auth_token)
        self.is_session_authenticated = True

        return response
    
if __name__ == '__main__':
    
    
    rs = FrameworkSession(base_url = 'http://localhost:8000/')
    
    
    password = {'username' : 'test12', 'password' : 'test12'}
    response = rs.login(username = 'test12', password = 'test12', override_id = 1)
    
    response = rs.get('profile/models/')
    
    print(response.json())
    