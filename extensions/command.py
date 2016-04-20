from subprocess import check_output
from subprocess import CalledProcessError
import logging


log = logging.getLogger(__name__)


def check_call(cmd, *args, **kwargs):
    log.info("$ %s" % " ".join(cmd))
    output = ""

    try:
        output = check_output(cmd, *args, **kwargs)
        return output
    except CalledProcessError:
        log.error(output)
        raise
