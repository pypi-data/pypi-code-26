import consul
import os


def consul_get_value(key):
    """
        environment variable configurations:
        CONSUL_ACCESS_TOKEN - required, sets the consul token
        CONSUL_HOST - sets the consul host to use default: consul.ops.tune.com
        CONSUL_SCHEME - http or https default: https
        CONSUL_PORT - port consul api is running on default: 443
        Args:
            key - string key to get from consul
        Return:
            value from consul
    """
    if 'CONSUL_ACCESS_TOKEN' not in os.environ:
        raise Exception('CONSUL_ACCESS_TOKEN not set in the environment, unable to finish call: consul_get_kv(%s)' % key)

    if 'CONSUL_HOST' not in os.environ:
        raise Exception('CONSUL_HOST not set in the environment, unable to finish call: consul_get_kv(%s)' % key)

    _, value_dict = consul.Consul(
        host=os.environ.get['CONSUL_HOST'],
        port=int(os.environ.get('CONSUL_PORT', 443)),
        scheme=os.environ.get('CONSUL_SCHEME', 'https'),
        token=os.environ['CONSUL_ACCESS_TOKEN']
    ).kv.get(key)
    if not value_dict:
        raise Exception("Key '%s' not found in consul" % key)

    return value_dict['Value']
