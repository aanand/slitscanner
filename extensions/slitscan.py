import logging
from math import ceil
import os
import tempfile

from PIL import Image
from PIL import ImageDraw


log = logging.getLogger(__name__)


def scan_frames(filenames, tmp_dir=None):
    frame_dir = tempfile.mkdtemp(dir=tmp_dir)
    log.info("Saving frames to {}".format(frame_dir))

    frames = [Image.open(f) for f in filenames]

    for index, file in enumerate(filenames):
        new_path = os.path.join(frame_dir, os.path.basename(file))
        new_frame = make_frame(frames, index)
        new_frame.save(new_path)
        yield new_path


def make_frame(frames, index):
    frame_size = frames[0].size
    frame_width, frame_height = frame_size
    band_height = max(1, int(round(float(frame_height) / len(frames))))
    num_bands = int(ceil(float(frame_height)/band_height))

    frame = Image.new("RGB", frame_size)

    for band_index in range(num_bands):
        overlay_index = (index + band_index) % len(frames)
        overlay_frame = frames[overlay_index]

        x0 = 0
        x1 = frame_width
        y0 = band_height * band_index
        y1 = y0 + band_height

        mask = Image.new("1", frame_size, color=1)
        draw = ImageDraw.Draw(mask)
        draw.rectangle([x0, y0, x1, y1], fill=0)

        frame = Image.composite(frame, overlay_frame, mask)

    return frame
