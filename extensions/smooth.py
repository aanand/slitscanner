from .command import check_call


def smooth_video(filename, destination, rate):
    check_call([
        'butterflow',
        '-v',   # verbose
        '-sw',  # software rendering
        '-sm',  # smooth video
        '-np',  # no preview
        '-r', rate,
        '-o', destination,
        filename,
    ])
