import os
import shutil
import config
import click
import requests

from tqdm import tqdm
from tinydb import TinyDB
from guessit import guessit
from slugify import slugify
from omdb import omdb_search


def get_file_ext(file_name):
    return os.path.splitext(file_name)[1]


def mkdir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(e)


def get_info(path):
    # Extract as much as possible from file name first
    video = dict(guessit(path))

    # Now try to get IMDB data
    omdb_info = omdb_search(video['title'], video.get('year'))
    video.update(omdb_info)

    return video


def desired_path(video):
    title = slugify(video['title'], to_lower=True, separator='_')
    year = str(video['year'])
    ext = video['container']
    screen_size = video['screen_size']
    video_format = video['format']

    # TODO: Make me customizable!
    return {
        'name': "{}.{}.{}.{}.{}".format(title, year, video_format, screen_size, ext),
        'path': os.path.join(config.LIBRARY, year, title)
    }


def download_file(url, dest):
    response = requests.get(url)
    with open(dest, 'wb') as dest:
        dest.write(response.content)


def copy_file(src, dest):
    try:
        shutil.copy(src, dest)
    except shutil.Error as e:
        print('Error: %s' % e)
    except IOError as e:
        print('Error: %s' % e.strerror)


@click.command()
@click.argument('movie', type=click.Path(), required=True)
def main(movie):
    # TODO: Better prompts, this is awful
    data = get_info(movie)
    print("The following is the extracted data for your movie:")
    for key, value in data.items():
        if key in ['title', 'released', 'genre']:
            print("{}: {}".format(key.capitalize(), value))
    dest = desired_path(data)
    print("\n\nThe file will move:")
    print("{} -> {}".format(os.path.abspath(movie), os.path.join(dest['path'], dest['name'])))
    if click.confirm("Is that ok?"):
        mkdir(dest['path'])
        copy_file(os.path.abspath(movie), os.path.join(dest['path'], dest['name']))
        download_file(data['poster'], os.path.join(dest['path'], 'poster.jpg'))


if __name__ == '__main__':
    main()
