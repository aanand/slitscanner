import tempfile

from .command import check_call


def smooth_video(filename, rate):
    _, out_filename = tempfile.mkstemp()

    check_call([
        'butterflow',
        '-v',   # verbose
        '-sw',  # software rendering
        '-sm',  # smooth video
        '-np',  # no preview
        '-r', rate,
        '-o', out_filename,
        filename,
    ])

    return out_filename
