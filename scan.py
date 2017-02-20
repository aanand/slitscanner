from botutils.gif import make_gif
from botutils.http import to_filename
from botutils.logging import start_logging
from botutils.tmpdir import tmpdir
from botutils.video import extract_frames
from botutils.video import get_dimensions
from botutils.video import get_frame_rate
from botutils.video import get_num_frames
from botutils.video import to_video

from extensions.slitscan import scan_frames
from extensions.smooth import smooth_video

import logging
import os
import sys

log = logging.getLogger(__name__)


# The minimum number of bands to split the image into.
MIN_BANDS = 100


# If for any reason we can't determine a file's frame rate,
# assume it's this.
DEFAULT_FRAME_RATE = 24.0


# If the frame rate is lower than this, we first
# double it with smoothing.
SMOOTHING_THRESHOLD = 20.0


# Maximum size, in bytes, of animated GIFs allowed by
# the Twitter API
MAX_GIF_SIZE = 5*1000*1000


def scan(url_or_filename, base_dir, destination):
    filename = to_filename(url_or_filename, os.path.join(base_dir, 'source'))
    filename = to_video(filename, os.path.join(base_dir, 'source.mp4'))

    filename, frame_rate = smooth(filename, base_dir)
    log.info("Frame rate: {}".format(frame_rate))

    num_frames = get_num_frames(filename)
    log.info("Num frames: {}".format(num_frames))

    (frame_width, frame_height) = get_dimensions(filename)
    log.info("Dimensions: {}x{}".format(frame_width, frame_height))

    num_bands = max(MIN_BANDS, min(frame_height, num_frames))
    log.info("Num bands: {}".format(num_bands))

    band_height = float(frame_height) / num_bands
    log.info("Band height: {}".format(band_height))

    frames = extract_frames(
        filename,
        os.path.join(base_dir, 'frames'),
        frame_rate,
    )

    frames = list(scan_frames(
        frames,
        os.path.join(base_dir, 'scanned'),
        num_bands=num_bands,
        band_height=band_height,
    ))

    make_gif(
        frames,
        destination,
        frame_rate=frame_rate,
        max_size=MAX_GIF_SIZE,
    )


def smooth(filename, base_dir):
    frame_rate = get_frame_rate(filename, DEFAULT_FRAME_RATE)

    if frame_rate >= SMOOTHING_THRESHOLD:
        return filename, frame_rate

    log.info("Frame rate is too low ({}) - smoothing".format(frame_rate))

    smoothed_filename = os.path.join(base_dir, 'source-2x.mp4')
    smooth_video(filename, smoothed_filename, '2x')

    return smoothed_filename, get_frame_rate(filename, DEFAULT_FRAME_RATE)


if __name__ == '__main__':
    start_logging()

    with tmpdir(delete=False) as base_dir:
        destination = os.path.join(base_dir, 'scanned.gif')
        scan(sys.argv[1], base_dir, destination)
        print(os.path.relpath(destination))
