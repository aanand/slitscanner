import logging
from math import ceil
import os
import tempfile

from PIL import Image
from PIL import ImageDraw


log = logging.getLogger(__name__)


BAND_PLATEAU = 64
MAX_WRAPAROUNDS = 2


def scan_frames(filenames, tmp_dir=None):
    frame_dir = tempfile.mkdtemp(dir=tmp_dir)

    frames = [Image.open(f).convert("RGB") for f in filenames]
    frame_size = frames[0].size
    frame_width, frame_height = frame_size

    if len(frames) < BAND_PLATEAU/MAX_WRAPAROUNDS:
        num_bands = len(frames)*MAX_WRAPAROUNDS
    elif len(frames) < BAND_PLATEAU:
        num_bands = BAND_PLATEAU
    else:
        num_bands = len(frames)

    log.info("Num frames: {}".format(len(frames)))
    log.info("Num bands: {}".format(num_bands))
    log.info("Saving frames to {}".format(frame_dir))

    for index, file in enumerate(filenames):
        new_path = os.path.join(frame_dir, os.path.basename(file))
        new_frame = make_frame(
            frames=frames,
            index=index,
            num_bands=num_bands,
        )
        new_frame.save(new_path)
        yield new_path


def make_frame(frames,
               index,
               num_bands):

    frame = Image.new("RGB", frames[0].size)
    band_height = float(frame.size[1]) / num_bands

    for band_index in range(num_bands):
        overlay_index = (index + band_index) % len(frames)
        overlay_frame = frames[overlay_index]

        x0 = 0
        x1 = frame.size[0]
        y0 = band_height * band_index
        y1 = y0 + band_height

        log.debug(
            "Overlaying frame #{} at ({}, {})-({}, {})"
            .format(overlay_index, x0, y0, x1, y1))

        mask = Image.new("1", frame.size, color=1)
        draw = ImageDraw.Draw(mask)
        draw.rectangle([x0, y0, x1, y1], fill=0)

        frame = Image.composite(frame, overlay_frame, mask)

    return frame
