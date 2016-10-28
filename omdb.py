import requests


def omdb_search(title, year=None):
    endpoint = 'http://www.omdbapi.com/'
    params = {'t': title.encode('ascii', 'ignore'),
              'plot': 'full',
              'type': 'movie',
              'tomatoes': 'true'}

    if year:
        params['y'] = year

    response = requests.get(endpoint, params=params)
    # Lower case all keys to prevent duplicate data
    return {key.lower(): value for key, value in response.json().items()}
