    
from masonite.routes import Get, Post
def routes(prefix='/dashboard'):
    return [
        Get().route('{}'.format(prefix), '/dashboard.controllers.DashboardController@show'),
        Get().route('{}/@model:string/@id:int'.format(prefix), '/dashboard.controllers.DashboardController@single'),
        Get().route('{}/@model:string'.format(prefix), '/dashboard.controllers.DashboardController@show_all'),
        Post().route('{}/@model:string/@id:int'.format(prefix), '/dashboard.controllers.DashboardController@update')
    ]