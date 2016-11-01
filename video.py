import os
from slugify import slugify


class Video:
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


class Movie(Video):
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


class Series(Video):
    def __init__(self, data):
        super().__init__(data)
        self.title = self.slugify(self.data['series'])
        self.ep_title = self.slugify(self.data['title'])

    def get_file_name(self):
        # TODO: Make formats configurable
        return "{}.s{:0>2}e{:0>2}.{}".format(self.title, self.data['season'],
                                             self.data['episode'],
                                             self.ep_title)
