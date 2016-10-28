import os
import config
from helpers import files


def mkdir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(e)


def walk_path(path):
    result = []
    path = os.path.abspath(path)
    for root, dirs, file_objs in os.walk(path):
        for file_name in file_objs:
            path = os.path.join(root, file_name)
            if os.path.getsize(path) > config.SCANNABLE_MIN_SIZE:
                if files.get_file_ext(file_name) in config.SCANNABLE_EXT:
                    result.append({
                        'path': root,
                        'file': file_name,
                    })
    return result
