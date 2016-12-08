import logging
import sys

from bot import SlitScanner
from bot import start_logging


log = logging.getLogger(__name__)
start_logging()

bot = SlitScanner()
old_value = bot.state['last_mention_id']
log.info("Current value: {}".format(old_value))
log.info("Current queue length: {}".format(len(bot.state['mention_queue'])))

if len(sys.argv) >= 2:
    new_value = sys.argv[1]
    log.info("New value: {}".format(new_value))
    bot.state['last_mention_id'] = new_value
    log.info("Clearing mention queue")
    bot.state['mention_queue'] = []
    log.info("Clearing recent replies")
    bot.state['recent_replies'] = []
    bot._save_state()
