import os
import json

import requests

from tqdm import tqdm
from tinydb import TinyDB
from guessit import guessit, jsonutils


DB_PATH = os.path.expanduser('~/.cinemabits.json')
SCANNABLE_MIN_SIZE = 25 * 1024 * 1024
SCANNABLE_EXT = (".3g2 .3gp .3gp2 .3gpp .60d .ajp .asf .asx .avchd .avi .bik .bix"
                 ".box .cam .dat .divx .dmf .dv .dvr-ms .evo .flc .fli .flic .flv"
                 ".flx .gvi .gvp .h264 .m1v .m2p .m2ts .m2v .m4e .m4v .mjp .mjpeg"
                 ".mjpg .mkv .moov .mov .movhd .movie .movx .mp4 .mpe .mpeg .mpg"
                 ".mpv .mpv2 .mxf .nsv .nut .ogg .ogm .omf .ps .qt .ram .rm .rmvb"
                 ".swf .ts .vfw .vid .video .viv .vivo .vob .vro .wm .wmv .wmx"
                 ".wrap .wvx .wx .x264 .xvid")


def get_file_ext(file_name):
    return os.path.splitext(file_name)[1]


def walk_path(path):
    result = []
    path = os.path.abspath(path)
    for root, dirs, files in os.walk(path):
        for file_name in files:
            path = os.path.join(root, file_name)
            if os.path.getsize(path) > SCANNABLE_MIN_SIZE:
                if get_file_ext(file_name) in SCANNABLE_EXT:
                    result.append({
                        'path': root,
                        'file': file_name,
                    })
    return result


def get_file_info(path):
    return guessit(path)


def omdb(title, year=None):
    endpoint = 'http://www.omdbapi.com/'
    params = {'t': title.encode('ascii', 'ignore'),
              'plot': 'full',
              'type': 'movie',
              'tomatoes': 'true'}

    if year:
        params['y'] = year

    response = requests.get(endpoint, params=params)
    return response.json()


def get_info(path):
    videos = walk_path(path)
    with tqdm(total=len(videos)) as pbar:
        for video in videos:
            file_info = get_file_info(video['file'])
            omdb_info = omdb(file_info['title'], file_info.get('year'))
            video.update(file_info)
            video.update(omdb_info)
            db_insert(video)
            pbar.update()


def db_insert(data, path=DB_PATH):
    db = TinyDB(path)
    db.insert(data)


get_info("/run/media/shahin/Entertainment/Movie")
