import logging
import re
import urllib

from bs4 import BeautifulSoup


log = logging.getLogger(__name__)

URL_PATTERN = re.compile(r'^https?://twitter\.com/(\w+)/status/(\d+)/photo/1$')


def get_gif_video_url(api, tweet):
    url = get_gif_page_url_climbing(api, tweet)
    if url is None:
        return None

    tweet_id = URL_PATTERN.match(url).group(2)

    log.info("Opening {}".format(url))
    html = urllib.urlopen(url).read()
    soup = BeautifulSoup(html)

    tag = soup.find('div', attrs={"data-tweet-id": tweet_id})
    if not tag:
        log.info("Couldn't find a div with data-tweet-id={} - giving up".format(repr(tweet_id)))
        return None

    match = re.search(r'https?://pbs\.twimg\.com/tweet_video_thumb/(.+)\.\w+', unicode(tag))
    if not match:
        log.info("Couldn't find a thumbnail URL - giving up")
        return None

    return "https://pbs.twimg.com/tweet_video/{}.mp4".format(match.group(1))


def get_gif_page_url_climbing(api, tweet):
    me = api.me()

    while True:
        url = get_gif_page_url(tweet)

        if url:
            return url

        if tweet.in_reply_to_status_id is None:
            break

        tweet = api.get_status(tweet.in_reply_to_status_id)

        # don't reply to myself
        if tweet.author.id == me.id:
            log.info("Found my own tweet ({}) - stopping".format(tweet_url(tweet)))
            break

        log.info("Climbing up to status {}".format(tweet_url(tweet)))


# We're looking for a media entity with a "http://twitter.com/.../photo/1" URL
def get_gif_page_url(tweet):
    log.info("Getting GIF page URL for {}".format(tweet_url(tweet)))

    for media in tweet.entities.get('media', []):
        if URL_PATTERN.match(media['expanded_url']):
            log.info("Found link: {}".format(media['expanded_url']))
            return media['expanded_url']

    log.info("Tweet has no media entity with a matching URL - giving up")
    return None


def tweet_url(tweet):
    return "http://twitter.com/{}/status/{}".format(tweet.author.screen_name, tweet.id)
