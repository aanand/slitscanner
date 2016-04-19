import logging

from .command import check_call


log = logging.getLogger(__name__)


def smooth_video(filename, destination, rate):
    output = check_call([
        'butterflow',
        '-v',   # verbose
        '-sw',  # software rendering
        '-sm',  # smooth video
        '-np',  # no preview
        '-r', rate,
        '-o', destination,
        filename,
    ])
    log.info(output)
