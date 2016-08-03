import os
import json

import config

from tqdm import tqdm
from tinydb import TinyDB
from guessit import guessit, jsonutils
from omdb import omdb_search


def get_file_ext(file_name):
    return os.path.splitext(file_name)[1]


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
            db_insert(video)
            pbar.update()


def db_insert(data, path=config.DB_PATH):
    db = TinyDB(path)
    db.insert(data)


get_info("/run/media/shahin/Entertainment/Movie")
