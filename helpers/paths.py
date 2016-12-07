import os
import config
from helpers import files


def mkdir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except Exception as e:
        print(e)


def walk_path(path, scannable_exts, min_size=0):
    result = []
    path = os.path.abspath(path)
    for root, dirs, file_objs in os.walk(path):
        for file_name in file_objs:
            path = os.path.join(root, file_name)
            if os.path.getsize(path) > min_size:
                if files.get_file_ext(file_name) in scannable_exts:
                    result.append({
                        'path': root,
                        'file': file_name,
                    })
    return result
