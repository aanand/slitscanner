import logging

from botutils.command import check_call
from botutils.command import CalledProcessError


log = logging.getLogger(__name__)


def smooth_video(filename, destination, rate):
    try:
        check_call(['which', 'butterflow'])
    except CalledProcessError:
        log.warn('butterflow not found - skipping smoothing step')
        check_call(['cp', filename, destination])
        return

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
