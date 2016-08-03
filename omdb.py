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
    return response.json()
