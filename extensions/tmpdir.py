from contextlib import contextmanager
import logging
from shutil import rmtree
from tempfile import mkdtemp


log = logging.getLogger(__name__)


@contextmanager
def tmpdir(*args, **kwargs):
    delete = kwargs.pop('delete', True)
    path = mkdtemp(*args, **kwargs)
    log.info("Created {}".format(path))
    try:
        yield path
    finally:
        if delete:
            log.info("Deleting {}".format(path))
            rmtree(path)
