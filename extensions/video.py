import logging
import os
import subprocess
import sys
import tempfile
import urllib
import json


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


def extract_frames(filename, frame_rate):
    if is_gif(filename):
        return extract_gif_frames(filename)
    else:
        return extract_movie_frames(filename, frame_rate)


def is_gif(filename):
    data = ffprobe(filename, 'format=format_name')
    return data['format']['format_name'] == "gif"


def extract_gif_frames(filename):
    frames_dir = tempfile.mkdtemp()
    check_call([
        'convert',
        '-coalesce',
        filename,
        os.path.join(frames_dir, '%04d.png')
    ])
    return sorted([os.path.join(frames_dir, f) for f in os.listdir(frames_dir)])


def extract_movie_frames(filename, frame_rate):
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


def check_call(cmd, *args, **kwargs):
    log.info("$ %s" % " ".join(cmd))
    output = ""

    try:
        output = subprocess.check_output(cmd, *args, **kwargs)
        return output
    except subprocess.CalledProcessError:
        log.error(output)
        raise
