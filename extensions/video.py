import logging
import os
import sys
import tempfile
import urllib
import json

from .command import check_call


log = logging.getLogger(__name__)


def make_gif(all_frames, frame_rate):
    _, gif_filename = tempfile.mkstemp('.gif')

    step = 1

    max_size = 5 * 1024 * 1024

    while True:
        frames = all_frames[::step]
        if len(frames) < 2:
            raise Exception("Can't make a file small enough (%d frames, step = %s)"
                % (len(all_frames), step))

        modified_frame_rate = int(round(frame_rate / step))

        cmd = [
            'convert',
            '-loop', '0',
            '-delay', '1x{}'.format(modified_frame_rate),
            '-layers', 'Optimize',
        ]
        cmd += frames
        cmd.append(gif_filename)
        check_call(cmd)

        if os.stat(gif_filename).st_size < max_size:
            break

        step += 1

    return gif_filename


def to_video(filename):
    if is_gif(filename):
        # Round width and height down to nearest even number
        (width, height) = get_dimensions(filename)
        width = width & ~1
        height = height & ~1

        _, out_filename = tempfile.mkstemp('.mp4')

        check_call([
            'ffmpeg',
            '-y',
            '-i', filename,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-s', '{}x{}'.format(width, height),
            out_filename,
        ])

        return out_filename

    return filename


def is_gif(filename):
    data = ffprobe(filename, 'format=format_name')
    return data['format']['format_name'] == "gif"


def extract_frames(filename, frame_rate):
    frames_dir = tempfile.mkdtemp()
    check_call([
        'ffmpeg',
        '-y',
        '-i', filename,
        '-r', str(frame_rate),
        os.path.join(frames_dir, '%04d.png'),
    ])
    return sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir)])


# Adapted from http://askubuntu.com/a/723362
def get_frame_rate(filename, default):
    rate = ffprobe_stream(filename, 'r_frame_rate').split('/')

    if len(rate)==1:
        return float(rate[0])
    if len(rate)==2:
        return float(rate[0])/float(rate[1])

    log.error("Unparseable output: {}".format(out))
    return default


def get_num_frames(filename):
    return int(ffprobe_stream(filename, 'nb_frames'))


def get_dimensions(filename):
    data = ffprobe(filename, 'stream=width,height')
    width = int(data['streams'][0]['width'])
    height = int(data['streams'][0]['height'])
    return (width, height)


def ffprobe_stream(filename, variable):
    data = ffprobe(filename, "stream={}".format(variable))
    return data['streams'][0][variable]


def ffprobe(filename, variables):
    output = check_call([
        'ffprobe',
        "-v", "0",
        "-select_streams", "v",
        "-print_format", "json",
        "-show_entries", variables,
        filename,
    ])
    return json.loads(output)
