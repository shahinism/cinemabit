import os
import config
import click
import requests
import dataset
import validators

from clint.textui import colored, puts
from helpers import files, paths
from video import Movie, Series, Info


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


def import_video(path, no_poster=False):
    # TODO: Subtitle support (if exist locally)
    vinfo = Info(path)
    data = vinfo.get()
    if not data:
        puts(colored.red('This video will not be imported!'))
        return

    puts(colored.white('The following data has been extracted:', bold=True))
    for key, value in data.items():
        if key in ['title', 'released', 'genre']:
            title = "{:>10}: ".format(key.capitalize())
            puts(colored.green(title) + colored.yellow(value))
    if data['type'] == 'episode':
        video = Series(data)
    else:
        video = Movie(data)

    dest = os.path.join(config.LIBRARY, video.get_desired_path())
    dest_dir = os.path.dirname(dest)
    data['path'] = dest

    puts(colored.white("\nThe video will archive as:", bold=True))
    puts(colored.green("{:>10}: ".format("From")) + colored.yellow(path))
    puts(colored.green("{:>10}: ").format("To") + colored.yellow(dest))
    if click.confirm("\nIs this OK?"):
        record(data)
        paths.mkdir(dest_dir)
        files.copy_file(path, dest)

        if not no_poster:
            poster_name = '{}.jpg'.format(video.get_poster_name())
            poster_path = os.path.join(dest_dir, poster_name)
            download_file(data['poster'], poster_path)


def import_tree(path, no_poster):
    videos = paths.walk_path(path)
    for video in videos:
        import_video(os.path.join(video['path'], video['file']))


@click.command()
@click.argument('target', type=click.Path(), required=True)
@click.option('--no-poster', help='do not get posters', default=False)
def main(target, no_poster):
    target = os.path.abspath(target)
    if os.path.isfile(target):
        import_video(target, no_poster)
    else:
        import_tree(target, no_poster)


if __name__ == '__main__':
    main()
