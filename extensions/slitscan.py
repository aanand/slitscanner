import logging
import os

from PIL import Image
from PIL import ImageDraw


log = logging.getLogger(__name__)


def scan_frames(filenames,
                destination,
                num_bands,
                band_height):

    if not os.path.exists(destination):
        os.makedirs(destination)

    frames = [Image.open(f).convert("RGB") for f in filenames]

    for index, file in enumerate(filenames):
        new_path = os.path.join(destination, os.path.basename(file))
        new_frame = make_frame(
            frames=frames,
            index=index,
            num_bands=num_bands,
            band_height=band_height,
        )
        new_frame.save(new_path)
        yield new_path


def make_frame(frames,
               index,
               num_bands,
               band_height):

    frame = Image.new("RGB", frames[0].size)

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
