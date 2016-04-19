from contextlib import contextmanager
from shutil import rmtree
from tempfile import mkdtemp


@contextmanager
def tmpdir(*args, **kwargs):
    delete = kwargs.pop('delete', True)
    path = mkdtemp(*args, **kwargs)
    try:
        yield path
    finally:
        if delete:
            rmtree(path)
