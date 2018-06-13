import requests

def talk_to_api(url, params=False, method=False, headers=False):
    '''
    connect to the external API for the resources
    if could not connect to the api return error
    '''

    try:
        if method == 'get':
            if not headers:

                response = requests.get(url, data=params)
            else:
                response = requests.get(url, data=params, headers=headers)
        else:

            if method == 'delete':
                response = requests.delete(url, data=params, headers=headers)
            else:

                if not headers:
                    response = requests.post(url, data=params)
                else:
                    response = requests.post(url, data=params, headers=headers)
        return response.text
    except requests.HTTPError as e:
        raise
    return False
