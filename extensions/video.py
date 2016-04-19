import logging
import os
import json

from .command import check_call


log = logging.getLogger(__name__)


def make_gif(all_frames, destination, frame_rate, max_size=None):
    step = 1

    while True:
        frames = all_frames[::step]
        if len(frames) < 2:
            raise Exception(
                "Can't make a file small enough ({} frames, step = {})"
                .format(len(all_frames), step))

        modified_frame_rate = int(round(frame_rate / step))

        cmd = [
            'convert',
            '-loop', '0',
            '-delay', '1x{}'.format(modified_frame_rate),
            '-layers', 'Optimize',
        ]
        cmd += frames
        cmd.append(destination)
        check_call(cmd)

        if max_size and os.stat(destination).st_size > max_size:
            step += 1
            continue

        return


def to_video(filename, destination):
    if is_gif(filename):
        # Round width and height down to nearest even number
        (width, height) = get_dimensions(filename)
        width = width & ~1
        height = height & ~1

        check_call([
            'ffmpeg',
            '-y',
            '-i', filename,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-s', '{}x{}'.format(width, height),
            destination,
        ])

        return destination

    return filename


def is_gif(filename):
    data = ffprobe(filename, 'format=format_name')
    return data['format']['format_name'] == "gif"


def extract_frames(filename, destination, frame_rate):
    if not os.path.exists(destination):
        os.makedirs(destination)

    check_call([
        'ffmpeg',
        '-y',
        '-i', filename,
        '-r', str(frame_rate),
        os.path.join(destination, '%04d.png'),
    ])

    return sorted([
        os.path.join(destination, f)
        for f in os.listdir(destination)
    ])


# Adapted from http://askubuntu.com/a/723362
def get_frame_rate(filename, default):
    rate = ffprobe_stream(filename, 'r_frame_rate').split('/')

    if len(rate) == 1:
        return float(rate[0])
    if len(rate) == 2:
        return float(rate[0])/float(rate[1])

    log.error("Unparseable output: {}".format(rate))
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
