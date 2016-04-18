import subprocess
import logging


log = logging.getLogger(__name__)


def check_call(cmd, *args, **kwargs):
    log.info("$ %s" % " ".join(cmd))
    output = ""

    try:
        output = subprocess.check_output(cmd, *args, **kwargs)
        return output
    except subprocess.CalledProcessError:
        log.error(output)
        raise
