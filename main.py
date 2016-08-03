import os


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


MOVIES = []
def walk_path(path):
    for root, dirs, files in os.walk(path):
        for file_name in files:
            path = os.path.join(root, file_name)
            if os.path.getsize(path) > SCANNABLE_MIN_SIZE:
                if get_file_ext(file_name) in SCANNABLE_EXT:
                    MOVIES.append(file_name)

walk_path("/run/media/shahin/Entertainment/Movie")
print(MOVIES)
