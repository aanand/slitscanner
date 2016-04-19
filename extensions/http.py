import logging
import urllib

log = logging.getLogger(__name__)


def to_filename(url_or_filename, destination):
    if url_or_filename.startswith(('http://', 'https://')):
        download(url_or_filename, destination)
        return destination

    return url_or_filename


def download(url, destination):
    log.info("Downloading %s", url)
    with open(destination, 'wb') as file:
        file.write(urllib.urlopen(url).read())
