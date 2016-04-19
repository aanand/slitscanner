#!/usr/bin/env python2
# -*- coding: utf-8 -*- #

from __future__ import unicode_literals

from twitterbot import FileStorage
from twitterbot import TwitterBot

from extensions.giftweet import get_gif_video_url
from extensions.http import to_filename
from extensions.slitscan import scan_frames
from extensions.smooth import smooth_video
from extensions.video import extract_frames
from extensions.video import get_dimensions
from extensions.video import get_frame_rate
from extensions.video import get_num_frames
from extensions.video import make_gif
from extensions.video import to_video

import arrow

import random
import os
import logging


log = logging.getLogger(__name__)


# The minimum number of bands to split the image into.
# If the number of frames is less than this, we first
# increase the framerate with smoothing.
MIN_BANDS = 100


def scan(url_or_filename):
    """
    Takes a URL or filename and returns a path to a .gif file
    containing a slit-scanned version of the video.
    """
    filename = to_filename(url_or_filename)
    filename = to_video(filename)

    num_frames = get_num_frames(filename)
    log.info("Num frames: {}".format(num_frames))

    if num_frames < MIN_BANDS:
        filename = smooth_video(filename, '2x')
        num_frames = get_num_frames(filename)
        log.info("Num frames after smoothing: {}".format(num_frames))

    (frame_width, frame_height) = get_dimensions(filename)
    log.info("Dimensions: {}x{}".format(frame_width, frame_height))

    num_bands = max(MIN_BANDS, min(frame_height, num_frames))
    log.info("Num bands: {}".format(num_bands))

    band_height = float(frame_height) / num_bands
    log.info("Band height: {}".format(band_height))

    frame_rate = get_frame_rate(filename, 24.0)
    log.info("Frame rate: {}fps".format(frame_rate))

    frames = extract_frames(filename, frame_rate)
    frames = list(scan_frames(
        frames,
        num_bands=num_bands,
        band_height=band_height,
    ))
    return make_gif(
        frames,
        frame_rate=frame_rate,
        max_size=3*1024*1024,
    )


class SlitScanner(TwitterBot):
    def bot_init(self):
        self.config['storage'] = FileStorage('/data')

        self.config['api_key'] = os.environ['TWITTER_CONSUMER_KEY']
        self.config['api_secret'] = os.environ['TWITTER_CONSUMER_SECRET']
        self.config['access_key'] = os.environ['TWITTER_ACCESS_TOKEN']
        self.config['access_secret'] = os.environ['TWITTER_ACCESS_TOKEN_SECRET']

        # use this to define a (min, max) random range of how often to tweet
        # e.g., self.config['tweet_interval_range'] = (5*60, 10*60) # tweets every 5-10 minutes
        self.config['tweet_interval_range'] = (1*60, 3*60*60)

        # only reply to tweets that specifically mention the bot
        self.config['reply_direct_mention_only'] = False

        # only include bot followers (and original tweeter) in @-replies
        self.config['reply_followers_only'] = False

        # fav any tweets that mention this bot?
        self.config['autofav_mentions'] = False

        # fav any tweets containing these keywords?
        self.config['autofav_keywords'] = []

        # follow back all followers?
        self.config['autofollow'] = True

        # ignore home timeline tweets which mention other accounts?
        self.config['ignore_timeline_mentions'] = False

        # ignore retweets in the home timeline
        self.config['ignore_timeline_retweets'] = True

        # max number of times to reply to someone within the moving window
        self.config['reply_threshold'] = 3

        # length of the moving window, in seconds
        self.config['recent_replies_window'] = 20*60

        # probability of replying to a matching timeline tweet
        self.config['timeline_reply_probability'] = float(os.environ.get('TIMELINE_REPLY_PROBABILITY') or '0.05')

        self.config['silent_mode'] = (int(os.environ.get('SILENT_MODE') or '1') != 0)

    def on_scheduled_tweet(self):
        pass

    def on_mention(self, tweet, prefix):
        if not self.check_reply_threshold(tweet, prefix):
            return

        try:
            self.reply_to_tweet(tweet, prefix)
        except Exception as e:
            self.log(str(e))
            return

    def on_timeline(self, tweet, prefix):
        if not self.check_reply_threshold(tweet, prefix):
            return

        if random.random() > self.config['timeline_reply_probability']:
            self.log("Failed dice roll. Not responding to {}".format(self._tweet_url(tweet)))
            return

        try:
            self.reply_to_tweet(tweet, prefix)
        except Exception as e:
            self.log(str(e))
            return

    def reply_to_tweet(self, tweet, prefix):
        video_url = get_gif_video_url(self.api, tweet)
        if video_url is None:
            self.log("Couldn't find a gif video URL for {}".format(self._tweet_url(tweet)))
            return

        text = prefix
        filename = scan(video_url)

        if self._is_silent():
            self.log("Silent mode is on. Would've responded to {} with '{} {}'".format(
                self._tweet_url(tweet), text, filename))
            return

        self.post_tweet(
            text,
            reply_to=tweet,
            media=filename,
        )
        self.update_reply_threshold(tweet, prefix)

    def _is_silent(self):
        return self.config['silent_mode']

    def check_reply_threshold(self, tweet, prefix):
        self.trim_recent_replies()
        screen_names = self.get_screen_names(prefix)
        over_threshold = [sn for sn in screen_names if self.over_reply_threshold(sn)]

        if len(over_threshold) > 0:
            self.log("Over reply threshold for {}. Not responding to {}".format(", ".join(over_threshold), self._tweet_url(tweet)))
            return False

        return True

    def over_reply_threshold(self, screen_name):
        replies = [r for r in self.recent_replies() if screen_name in r['screen_names']]
        return len(replies) >= self.config['reply_threshold']

    def update_reply_threshold(self, tweet, prefix):
        screen_names = self.get_screen_names(prefix)

        self.recent_replies().append({
            'created_at': arrow.utcnow(),
            'screen_names': screen_names,
        })

        self.log("Updated recent_replies: len = {}".format(len(self.recent_replies())))

    def get_screen_names(self, prefix):
        return [sn.replace('@', '') for sn in prefix.split()]

    def trim_recent_replies(self):
        len_before = len(self.recent_replies())
        now = arrow.utcnow()
        self.state['recent_replies'] = [
            r for r in self.recent_replies()
            if (now - r['created_at']).seconds < self.config['recent_replies_window']
        ]
        self.log("Trimmed recent_replies: {} -> {}".format(len_before, len(self.recent_replies())))

    def recent_replies(self):
        if 'recent_replies' not in self.state:
            self.state['recent_replies'] = []
        return self.state['recent_replies']


def start_logging():
    stderr = logging.StreamHandler()
    stderr.setLevel(logging.INFO)
    stderr.setFormatter(logging.Formatter(fmt='%(levelname)8s: %(message)s'))

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(stderr)


if __name__ == '__main__':
    start_logging()
    bot = SlitScanner()
    bot.run()
