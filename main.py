import re
import os
import config
import click
import requests
import dataset
import validators

from guessit import guessit
from slugify import slugify
from helpers import omdb, files, paths
from video import Movie, Series


def extract_imdbid(string):
    match = re.search('(tt\d+)', string)
    return match.groups()[0] if match else None


def get_info_by_id():
    userinput = click.prompt('Insert IMDB ID or URL', type=str)
    imdbid = extract_imdbid(userinput)
    if imdbid:
        return omdb.find(imdbid)
    else:
        return get_info_by_id()


def get_info(path):
    # Extract as much as possible from file name first
    video = dict(guessit(path))

    # Now try to get IMDB data
    if video['type'] == 'episode':
        video['series'] = video['title']
        omdb_info = omdb.search(
            video['title'],
            video.get('year'),
            season=video['season'],
            episode=video['episode'])
    else:
        omdb_info = omdb.search(
            video['title'], video.get('year'), type_='movie')

    if omdb_info.get('response') == 'False':
        error = omdb_info.get('error', 'Unknown')
        print("Couldn't find IMDB data. error: {}".format(error))

        if click.confirm("Can you provide an IMDB ID or URL for this title?"):
            omdb_info = get_info_by_id()

    if omdb_info.get('response') == 'True':
        video.update(omdb_info)

    return video


def slugify_it(string):
    return slugify(string, to_lower=True, separator='_')


def download_file(url, dest):
    if not validators.url(url):
        print("Not a valid image url: {}".format(url))
        return
    response = requests.get(url)
    with open(dest, 'wb') as dest:
        dest.write(response.content)


def record(data):
    data = {k: str(v) for k, v in data.items()}
    db = dataset.connect('sqlite:///{}'.format(config.DB_PATH))
    table = db.get_table('movies')

    # Bugfix, it's not working!
    if table.find_one(imdbid=data.get('imdbid')):
        table.update(data, ['imdbid'])
    table.insert(data)


def import_video(movie, no_poster=False):
    # TODO: Subtitle support (if exist locally)
    # TODO: Better prompts, this is awful
    data = get_info(movie)
    print("The following is the extracted data for your movie:")
    for key, value in data.items():
        if key in ['title', 'released', 'genre']:
            print("{}: {}".format(key.capitalize(), value))
    if data['type'] == 'episode':
        video = Series(data)
    else:
        video = Movie(data)

    dest = os.path.join(config.LIBRARY, video.get_desired_path())
    data['path'] = dest
    print("\n\nThe file will move:")
    print("From:\n    {}\nTo:\n    {}".format(movie, dest))
    if click.confirm("Is that ok?"):
        record(data)

        paths.mkdir(dest['path'])
        files.copy_file(movie, dest)

        if not no_poster:
            poster_name = '{}.jpg'.format(video.get_poster_name())
            download_file(data['poster'],
                          os.path.join(dest['path'], poster_name))


def import_tree(path, no_poster):
    videos = paths.walk_path(path)
    for video in videos:
        import_video(os.path.join(video['path'], video['file']))


@click.command()
@click.argument(
    'target',
    type=click.Path(),
    required=True)
@click.option('--no-poster', help='do not get posters', default=False)
def main(target, no_poster):
    target = os.path.abspath(target)
    if os.path.isfile(target):
        import_video(target, no_poster)
    else:
        import_tree(target, no_poster)


if __name__ == '__main__':
    main()
