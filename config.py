import os


LIBRARY = "/run/media/shahin/Entertainment/Media"
DB_PATH = os.path.expanduser('~/.cinemabits.db')
VIDEO_MIN_SIZE = 25 * 1024 * 1024
VIDEO_EXT = (
    ".3g2 .3gp .3gp2 .3gpp .60d .ajp .asf .asx .avchd .avi .bik .bix"
    ".box .cam .dat .divx .dmf .dv .dvr-ms .evo .flc .fli .flic .flv"
    ".flx .gvi .gvp .h264 .m1v .m2p .m2ts .m2v .m4e .m4v .mjp .mjpeg"
    ".mjpg .mkv .moov .mov .movhd .movie .movx .mp4 .mpe .mpeg .mpg"
    ".mpv .mpv2 .mxf .nsv .nut .ogg .ogm .omf .ps .qt .ram .rm .rmvb"
    ".swf .ts .vfw .vid .video .viv .vivo .vob .vro .wm .wmv .wmx"
    ".wrap .wvx .wx .x264 .xvid")
SUBTITLE_EXT = (".srt", ".sub", ".idx")
