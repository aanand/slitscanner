from extensions.processor import Processor
import sys
import logging

stderr = logging.StreamHandler()
stderr.setLevel(logging.DEBUG)
stderr.setFormatter(logging.Formatter(fmt='%(levelname)8s: %(message)s'))

root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(stderr)

url = sys.argv[1]

print Processor().scan_url(url)
