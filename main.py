import os
import config
import click
import requests
import dataset
import validators

from colorama import init, Fore
from helpers import files, paths
from video import Movie, Series, VideoInfo

init(autoreset=True)


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
    vinfo = VideoInfo(path)
    data = vinfo.get_info()
    if not data:
        print(Fore.BLUE + "This video will not be imported!")
        return

    print(Fore.BLUE + "The following has been extracted data:\n")
    for key, value in data.items():
        if key in ['title', 'released', 'genre']:
            print("{}{:>10}: {}{}".format(Fore.GREEN,
                                          key.capitalize(), Fore.RESET, value))
    if data['type'] == 'episode':
        video = Series(data)
    else:
        video = Movie(data)

    dest = os.path.join(config.LIBRARY, video.get_desired_path())
    dest_dir = os.path.dirname(dest)
    data['path'] = dest
    print("{0}\nThis video will archive as:".format(Fore.YELLOW))
    print("{0}From:\n    {1}".format(Fore.RED, path))
    print("{0}To:\n    {1}\n".format(Fore.GREEN, dest))
    if click.confirm("Is this OK?"):
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
