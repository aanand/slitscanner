import logging
import sys

from bot import SlitScanner
from bot import start_logging


log = logging.getLogger(__name__)
start_logging()

bot = SlitScanner()
old_value = bot.state['last_mention_id']
log.info("Current value: {}".format(old_value))

if len(sys.argv) >= 2:
    new_value = sys.argv[1]
    log.info("New value: {}".format(new_value))
    bot.state['last_mention_id'] = new_value
    bot._save_state()
