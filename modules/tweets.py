from datetime import datetime
import pandas as pd

import tweepy

DEBUG = False

def get_twitter_api_obj(keys=None):
    """Creating Tweepy API object using provided keys."""
    if not keys:
        keys = pd.read_csv('res/Test-Twitter-Keys_NO_GIT.csv')
    # Creating the authentication object
    auth = tweepy.OAuthHandler(keys.consumer_key[0], keys.consumer_secret[0])
    # Setting your access token and secret
    auth.set_access_token(keys.access_token[0], keys.access_token_secret[0])

    # Creating the API object while passing in auth information (notifications gives wait in secs)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    return api


def get_tweets_from_search(api, query, language="en"):
    """Searching for tweets with provided query and with optional language selection."""
    # get 500 tweets from 5 pages as we get max 100 tweets per page

    # Configure number of Tweets to fetch and fetching them.
    (pages, count) = (1, 20) if DEBUG else (2, 100)
    max_pages = pages
    cursor = tweepy.Cursor(api.search, q=query, lang=language, count=count).pages(max_pages)

    # Processing response
    tweets = []
    tw_texts = []
    for i, page in enumerate(cursor):
        now = datetime.now().strftime('%H:%M:%S')
        print('At {}: Obtained {} tweet pages for {!r}.'.format(now, str(i + 1), query))
        for tweet in page:
            tweets.append(tweet)

    print('Found {} tweets for {!r}.'.format(len(tweets), query))
    return tweets