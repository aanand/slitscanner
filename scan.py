from bot import start_logging
from extensions.processor import Processor
import sys

start_logging()

target = sys.argv[1]

if target.startswith(('http://', 'https://')):
    print Processor().scan_url(target)
else:
    print Processor().scan_file(target)
