import requests

ENDPOINT = 'http://www.omdbapi.com/'


def lower_dict_keys(dictionary):
    return {key.lower(): value for key, value in dictionary.items()}


def search(title, year=None, type_='movie'):
    params = {'t': title.encode('ascii', 'ignore'),
              'plot': 'full',
              'type': type_,
              'tomatoes': 'true'}

    if year:
        params['y'] = year

    response = requests.get(ENDPOINT, params=params)
    # Lower case all keys to prevent duplicate data
    return lower_dict_keys(response.json())


def find(imdbid):
    params = {
        'i': imdbid,
        'plot': 'full',
        'tomatoes': 'true'
    }

    response = requests.get(ENDPOINT, params=params)
    # Lower case all keys to prevent duplicate data
    return lower_dict_keys(response.json())
