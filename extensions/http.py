import tempfile
import urllib
import logging

log = logging.getLogger(__name__)


def to_filename(url_or_filename):
    if url_or_filename.startswith(('http://', 'https://')):
        return download(url_or_filename)

    return url_or_filename


def download(url):
    """
    Takes a video URL and returns a path to a .gif file
    containing a moshed version of the video.
    """
    log.info("Downloading %s", url)
    file = tempfile.NamedTemporaryFile(delete=False)
    file.write(urllib.urlopen(url).read())
    file.close()
    return file.name
