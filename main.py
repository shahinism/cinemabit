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


class Archiver(object):
    def __init__(self, path, video, poster=True, subtitle=True):
        self.old_path_dir = path
        self.old_video_name = video
        self.old_video_path = os.path.join(path, video)
        self.new_path_dir = None
        self.new_video_name = None
        self.new_video_path = None
        self.poster = poster
        self.subtitle = subtitle
        self.data = self.get_info()
        self.dest = None
        self.video = None

    def get_info(self):
        return Info(self.old_video_path).get()

    def set_dest(self):
        self.new_path = os.path.join(config.LIBRARY, self.video.get_new_path())
        self.new_video_name = self.video.get_video_name()
        self.new_video_path = self.data['path'] = os.path.join(self.new_path, self.new_video_name)

    def cp_video(self):
        files.copy_file(self.old_video_path, self.new_video_path)

    def set_video_type(self):
        if self.data['type'] == 'episode':
            self.video = Series(self.data)
        else:
            self.video = Movie(self.data)
        self.set_dest()

    def get_poster(self):
        # TODO: Support local posters
        poster_path = os.path.join(self.new_path, self.video.get_poster_name())
        download_file(self.data['poster'], poster_path)

    def save_video(self):
        # TODO: Subtitle support (if exist locally)
        if not self.data:
            puts(colored.red('This video will not be imported!'))
            return

        puts(colored.white('The following data has been extracted:', bold=True))
        for key, value in self.data.items():
            if key in ['title', 'released', 'genre']:
                title = "{:>10}: ".format(key.capitalize())
                puts(colored.green(title) + colored.yellow(value))

        self.set_video_type()
        puts(colored.white("\nThe video will archive as:", bold=True))
        puts(colored.green("{:>10}: ".format("From")) + colored.yellow(self.old_video_path))
        puts(colored.green("{:>10}: ").format("To") + colored.yellow(self.new_video_path))
        if click.confirm("\nIs this OK?"):
            record(self.data)
            self.cp_video()

            if self.poster:
                self.get_poster()

def import_tree(path, poster):
    videos = paths.walk_path(path)
    for video in videos:
        Archiver(video['path'], video['file'], poster).save_video()


@click.command()
@click.argument('target', type=click.Path(), required=True)
@click.option('--no-poster', help='do not get posters', default=False)
def main(target, no_poster):
    target = os.path.abspath(target)
    if os.path.isfile(target):
        import_video(target, not no_poster)
    else:
        import_tree(target, not no_poster)


if __name__ == '__main__':
    main()
