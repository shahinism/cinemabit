import os
import json

import config

from shutil import copyfile

from tqdm import tqdm
from tinydb import TinyDB
from guessit import guessit, jsonutils
from slugify import slugify
from omdb import omdb_search


def get_file_ext(file_name):
    return os.path.splitext(file_name)[1]


def mkdir(path):
    try:
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


def get_file_info(path):
    result = guessit(path)
    encoder = jsonutils.GuessitEncoder()
    return json.loads(encoder.encode(result))


def get_info(path):
    videos = walk_path(path)
    with tqdm(total=len(videos)) as pbar:
        for video in videos:
            file_info = get_file_info(video['file'])
            omdb_info = omdb_search(file_info['title'], file_info.get('year'))
            video.update(file_info)
            video.update(omdb_info)
            pbar.update()

    return videos


def db_insert(data, path=config.DB_PATH):
    db = TinyDB(path)
    db.insert(data)


def find_video_path(video):
    title = slugify(video['title'], to_lower=True, separator='_')
    year = video['Year']
    ext = video['container']

    # TODO: Make me customizable!
    dest_name = title + "_" + year + "." + ext
    dest_path = os.path.join(config.LIBRARY, year, title)

    curr_name = video['file']
    curr_path = video['path']
    mkdir(dest_path)
    copyfile(os.path.join(curr_path, curr_name), os.path.join(dest_path, dest_name))

    return

def import_video(video):
    db_insert(video)
    path = find_video_path(video)


def scan_videos(path):
    videos = get_info(path)
    for video in tqdm(videos):
        import_video(video)

scan_videos("/run/media/shahin/Entertainment/Movie/2009/A_perfect_getaway_2009")
