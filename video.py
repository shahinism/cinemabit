import re
import os
import click

from clint.textui import colored, puts
from guessit import guessit
from slugify import slugify
from helpers import omdb


class _Video:
    def __init__(self, data):
        self.data = data
        self.video_type = data['type']
        self.ext = self.data['container']

    @staticmethod
    def slugify(string):
        return slugify(string, to_lower=True, separator='_')

    def get_desired_path(self):
        file_name = '{}.{}'.format(self.get_file_name(), self.ext)
        if self.video_type == 'episode':
            path = os.path.join('Series', self.title, file_name)
        else:
            path = os.path.join('Movies', self.year, self.title, file_name)

        return path

    def get_poster_name(self):
        if self.video_type == 'episode':
            return self.get_file_name()
        else:
            return 'poster'


class Movie(_Video):
    def __init__(self, data):
        super().__init__(data)
        self.title = self.slugify(self.data['title'])
        self.year = str(self.data.get('year', 'unknown'))

    def get_file_name(self):
        name = "{}.{}".format(self.title, self.year)
        if self.data.get('screen_size'):
            name = "{}.{}".format(name, self.data['screen_size'])
        if self.data.get('format'):
            name = "{}.{}".format(name, self.data['format'])
        if self.data.get('cd'):
            name = "{}.cd_{}".format(name, self.data['cd'])

        return name


class Series(_Video):
    def __init__(self, data):
        super().__init__(data)
        self.title = self.slugify(self.data['series'])
        self.ep_title = self.slugify(self.data['title'])

    def get_file_name(self):
        # TODO: Make formats configurable
        return "{}.s{:0>2}e{:0>2}.{}".format(self.title, self.data['season'],
                                             self.data['episode'],
                                             self.ep_title)


class Info:
    def __init__(self, path):
        self.path = path
        self.data = self.guess()
        self.updated = False

    def guess(self):
        return dict(guessit(self.path))

    @staticmethod
    def get_imdbid():
        userinput = click.prompt('Insert IMDB ID or URL', type=str)
        match = re.search('(tt\d+)', userinput)
        return match.groups()[0] if match else None

    def update_info(self):
        self.updated = True
        if self.data['type'] == 'episode':
            self.data['series'] = self.data['title']
            omdb_info = omdb.search(
                self.data['title'],
                self.data.get('year'),
                season=self.data['season'],
                episode=self.data['episode'])
        else:
            omdb_info = omdb.search(
                self.data['title'], self.data.get('year'), type_='movie')

        self.data.update(omdb_info)

    def update_info_by_id(self):
        imdbid = self.get_imdbid()
        if not imdbid:
            return self.update_by_id()

        omdb_info = omdb.find(imdbid)
        self.data.update(omdb_info)

    def get(self):
        if not self.updated:
            self.update_info()

        if self.data.get('response') == 'True':
            return self.data

        error = self.data.get('error', 'Unknown')
        puts(colored.yellow("Couldn't find IMDB data. error: ") + colored.red(error))
        if click.confirm("Can you provide an IMDB ID or URL for this title?"):
            self.update_info_by_id()
            return self.get_info()

        return None
