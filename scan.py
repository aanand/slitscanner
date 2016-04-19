from bot import scan
from bot import start_logging
from extensions.tmpdir import tmpdir

import os
import sys

start_logging()

with tmpdir(delete=False) as base_dir:
    destination = os.path.join(base_dir, 'scanned.gif')
    scan(sys.argv[1], base_dir, destination)
    print(destination)
