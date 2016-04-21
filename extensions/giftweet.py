import logging
import re

from tweepy.error import TweepError


log = logging.getLogger(__name__)

URL_PATTERN = re.compile(r'^https?://twitter\.com/(\w+)/status/(\d+)/photo/1$')


def get_gif_video_url_climbing(api, tweet):
    me = api.me()

    while True:
        url = get_gif_video_url(api, tweet)

        if url:
            return url

        if tweet.in_reply_to_status_id is None:
            break

        try:
            tweet = api.get_status(tweet.in_reply_to_status_id)
        except TweepError:
            log.info("Next tweet up the chain has been deleted - stopping")
            break

        # don't reply to myself
        if tweet.author.id == me.id:
            log.info(
                "Found my own tweet ({}) - stopping"
                .format(tweet_url(tweet)))
            break

        log.info("Climbing up to status {}".format(tweet_url(tweet)))


def get_gif_video_url(api, tweet):
    log.info("Getting GIF video URL for {}".format(tweet_url(tweet)))

    if not hasattr(tweet, 'extended_entities'):
        log.info("Tweet has no extended_entities attribute - giving up")
        return None

    extended_entities = tweet.extended_entities
    log.debug("Extended entities: {}".format(extended_entities))

    for media in extended_entities.get('media', []):
        if media.get('type') == 'animated_gif':
            return media['video_info']['variants'][0]['url']

    log.info("Tweet has no media entity with a matching URL - giving up")
    return None


def tweet_url(tweet):
    return "http://twitter.com/{}/status/{}".format(
        tweet.author.screen_name, tweet.id)
