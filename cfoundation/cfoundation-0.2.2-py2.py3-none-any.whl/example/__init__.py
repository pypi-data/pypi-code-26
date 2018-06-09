from . import controllers, services
from cfoundation import create_app

App = create_app(
    name='cfoundation-greet',
    controllers=controllers,
    services=services,
    conf={
        'english': 'hello',
        'german': 'halo',
        'spanish': 'hallo',
        'french': 'bonjour'
    }
)
