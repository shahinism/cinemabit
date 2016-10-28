import os
import shutil
import config
import click
import requests
import dataset
import validators

from tqdm import tqdm
from guessit import guessit
from slugify import slugify
from omdb import omdb_search


def copyfileobj(fsrc, fdst, source_size, length=16*1024):
    with tqdm(total=source_size, unit='B', unit_scale=True) as pbar:
        while True:
            buf = fsrc.read(length)
            if not buf:
                break
            fdst.write(buf)
            pbar.update(len(buf))


def copy_file(src, dst):
    if shutil._samefile(src, dst):
        raise shutil.SameFileError("{!r} and {!r} are the same file".format(src, dst))

    else:
        source_size = os.stat(src).st_size
        with open(src, 'rb') as fsrc:
            with open(dst, 'wb') as fdst:
                copyfileobj(fsrc, fdst, source_size)

    return dst


def get_file_ext(file_name):
    return os.path.splitext(file_name)[1]


def mkdir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(e)


def walk_path(path):
    result = []
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for file_name in files:
            path = os.path.join(root, file_name)
            if os.path.getsize(path) > config.SCANNABLE_MIN_SIZE:
                if get_file_ext(file_name) in config.SCANNABLE_EXT:
                    result.append({
                        'path': root,
                        'file': file_name,
                    })
    return result


def get_info(path):
    # Extract as much as possible from file name first
    video = dict(guessit(path))

    # Now try to get IMDB data
    omdb_info = omdb_search(video['title'], video.get('year'))
    video.update(omdb_info)

    return video


def desired_path(video):
    title = slugify(video['title'], to_lower=True, separator='_')
    # TODO: Make it possible to edit
    year = str(video.get('year', 'unknown'))
    ext = video['container']

    name = "{}.{}".format(title, year)
    if video.get('screen_size'):
        name = "{}.{}".format(name, video['screen_size'])
    if video.get('format'):
        name = "{}.{}".format(name, video['format'])
    if video.get('cd'):
        name = "{}.cd_{}".format(name, video['cd'])

    # TODO: Make me customizable!
    return {
        'name': "{}.{}".format(name, ext),
        'path': os.path.join(config.LIBRARY, year, title)
    }


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
    dest = desired_path(data)
    data['path'] = os.path.join(dest['path'])
    print("\n\nThe file will move:")
    print("{} -> {}".format(os.path.abspath(movie), os.path.join(dest['path'], dest['name'])))
    if click.confirm("Is that ok?"):
        record(data)

        mkdir(dest['path'])
        copy_file(os.path.abspath(movie), os.path.join(dest['path'], dest['name']))

        if not no_poster:
            download_file(data['poster'], os.path.join(dest['path'], 'poster.jpg'))


def import_tree(path, no_poster):
    videos = walk_path(path)
    for video in videos:
        import_video(os.path.join(video['path'], video['file']))


@click.command()
@click.option(
    '-v',
    '--video',
    help='single target video file to import',
    type=click.Path()
)
@click.option(
    '-d',
    '--directory',
    help='target directory of movies to import recursively',
    type=click.Path()
)
@click.option(
    '--no-poster',
    help='do not get posters',
    default=False
)
def main(video, directory, no_poster):
    if video:
        import_video(video, no_poster)
    elif directory:
        import_tree(directory, no_poster)
    else:
        print("Please give a video (-v) or a directory of movies (-d) to import.")
        print("Look at --help for more information.")

if __name__ == '__main__':
    main()