"""Prototype Product to present happy-ness of Twitter users to a topic, object or company."""
import argparse
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from datetime import datetime
from collections import namedtuple

from modules.sentiment import analyze
from modules.tweets import get_twitter_api_obj, get_tweets_from_search

DEBUG = True


def plot_sent_vs_time(df):
    """Takes a DataFrame: index = created date, sentiment score, magnitude
    plots score against time, marker size = magnitude."""

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 8))

    # drawing a scatter plot of sentiment score against time, with magnitude driving marker size
    ax1.scatter(df.index, df.score, c=df.score, s=(df.magnitude + 0.1) * 100,
                cmap='RdYlGn', vmin=-1, vmax=1, label='Sentiment Score')

    # calculating spacing, group size, and labeling depending on time spread of data
    spread = (max(df.index) - min(df.index))
    padding = [(timedelta(minutes=5), pd.DateOffset(seconds=10), df.index.second, 'second'),
               (timedelta(minutes=30), pd.DateOffset(seconds=30), df.index.minute, 'minute'),
               (timedelta(hours=5), pd.DateOffset(minutes=5), df.index.hour, 'hour'),
               (timedelta(days=1), pd.DateOffset(minutes=15), df.index.hour, 'hour'),
               (timedelta(days=7), pd.DateOffset(hours=1), df.index.day, 'day'),
               (timedelta(days=14), pd.DateOffset(hours=4), df.index.day, 'day'),
               (timedelta(weeks=4), pd.DateOffset(days=1), df.index.week, 'week')]
    margin, group, lbl = next(((v[1], v[2], v[3]) for i, v in enumerate(padding) if v[0] > spread),
                              (pd.DateOffset(days=3), df.index.week, 'week'))
    print('Tweets are spread over {}, so padding scatter chart by {} and grouping box chart by {}.'.format(
        spread, margin, lbl))

    ax1.set_xlim([min(df.index) - margin, max(df.index) + margin])
    ax1.set_ylim([-1, 1])
    ax1.set_axisbelow(True)
    ax1.grid()

    # labeling
    ax1.legend(loc='upper right')
    ax1.set_xlabel("Tweet 'created at' time")
    ax1.set_ylabel('Tweet sentiment score')
    ax1.set_title('Sentiment Score for Tweets against time. Size of dot is' + \
                  ' magnitude, a measure of emotion in Tweet')

    # drawing a box plot to provide statistical summary for tweet data group by group size
    boxprops = dict(color='oldlace')
    medianprops = dict(linewidth=1, linestyle='--')
    sns.boxplot(group, df.score, ax=ax2, showmeans=True, boxprops=boxprops,
                medianprops=medianprops)

    # labeling
    ax2.set_ylim([-1, 1])
    ax2.set_axisbelow(True)
    ax2.grid()
    ax2.set_xlabel("Tweets agregated by {}".format(lbl))
    ax2.set_ylabel('Tweet sentiment score')
    ax2.set_title('Box plot statistics (Min, Max, Mean, Median, 25th and 75th %ile)' + \
                  ' of Sentiment Score showing trend over time')

    plt.show()


def swarm_and_hist(df):
    """Finds and prints the tweets with the highest sentiment scores."""
    df['score_str'] = round(df['score'], 2)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # drawing a swarmplot of sentiment score against sentiment magnitude
    sns.swarmplot(x='score_str', y='magnitude', data=df, ax=ax1)

    ax1.set_xlabel("Sentiment Score")
    ax1.set_ylabel('Sentiment Magnitude')
    ax1.set_ylim([0, 1])
    ax1.set_title('Swarm plot of Tweet Sentiment against Tweet Magnitude.')

    # drawing a histogram of tweets sentiment distribution
    ax2.hist(df.score, bins=15, alpha=0.5)
    ax2.set_xlim([-1, 1])
    ax2.set_xlabel("Sentiment Score")
    ax2.set_ylabel('Number of Tweets')
    ax2.set_title('Histogram of Tweet Sentiment.')
    plt.show()


def summarise_extreme_tweets(tweets, sentiments):
    """Finds and prints the tweets with the highest sentiment scores."""
    df = pd.DataFrame(sentiments)
    most_positive = df.loc[df.score == df.max()['score']]
    most_negative = df.loc[df.score == df.min()['score']]
    print('The most positive tweets:')
    for i in most_positive.index:
        summarise_tweet(tweets[i], sentiments[i].score, sentiments[i].magnitude)
    print('\n\nThe most negative tweets:')
    for i in most_negative.index:
        summarise_tweet(tweets[i], sentiments[i].score, sentiments[i].magnitude)


def summarise_tweet(t,s,m):
    """Prints a summary of a tweet and its sentiment."""
    if not t.in_reply_to_screen_name:
        print('\nAt {}, {}, (@{}) tweeted:'.format(
            t.created_at, t.user.name, t.user.screen_name, t.in_reply_to_screen_name))
    else:
        print('\nAt {}, {}, (@{}) tweeted in reply to {}:'.format(
            t.created_at, t.user.name, t.user.screen_name, t.in_reply_to_screen_name))
    # showing full text in command line
    text = t.text if hasattr(t, 'text') else t.full_text
    print('    {}'.format(text))
    print('Sentiment score: {:.1f}, Magnitude: {:.1f}'.format(s,m))


def get_data(search_term):
    """Uses Twitter APIs to get tweets for provided search term.
    Uses Google Sentiment API to analyse Tweet sentiment."""

    # authenticating a tweepy api object
    current_api = get_twitter_api_obj()
    # searching for tweets of interest
    tweets = get_tweets_from_search(current_api, search_term)

    # running Google sentiment analysis on found tweets
    tw_texts = [t.text if hasattr(t, 'text') else t.full_text for t in tweets]
    sentiments = analyze(tw_texts)
    return tweets, sentiments


def present(tweets, sentiments):
    """Summarizes key aspects of the data and presents it."""
    dfp = pd.DataFrame(sentiments)
    print('The {} most positive tweets have a sentiment score of {:.2f}'.format(
        len(dfp.loc[dfp.score == dfp.max()['score']]), dfp.max()['score']))
    print('The {} most negative tweets have sentiment score of {:.2f}'.format(
        len(dfp.loc[dfp.score == dfp.min()['score']]), dfp.min()['score']))

    dfg = pd.DataFrame(sentiments)
    dfg['created_at'] = pd.DataFrame([t.created_at for t in tweets])
    dfg.set_index('created_at', inplace=True)
    plot_sent_vs_time(dfg)
    swarm_and_hist(dfg)


def main(options):
    """Main program execution"""

    tweets, sentiments = get_data(options.search_term)
    present(tweets, sentiments)
    summarise_extreme_tweets(tweets, sentiments)


if __name__ == '__main__':
    """Enabling command line running"""

    p = argparse.ArgumentParser(description="Search for matching Tweats, measure their sentiment (aka happiess).")

    p.add_argument("search_term", help="What product or company do you want to search Twitter for?")
    main(p.parse_args())