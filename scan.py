from bot import scan
from bot import start_logging
import sys

start_logging()

print scan(sys.argv[1])
