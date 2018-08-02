import os
from collections import namedtuple

from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

PATH = '/Users/alisonkline/Code/'
GOOGLE_KEY_FILE_NAME = 'TwHappy/res/tw-happy-1531935955393-fb5eb8b48a61_NO_GIT.json'

# setting up authentication of the Google Cloud API
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = PATH + GOOGLE_KEY_FILE_NAME

DEBUG = False

def analyze(tw_texts):
    """Run a sentiment analysis request on a set of tweets."""
    client = language.LanguageServiceClient()
    sentiment = namedtuple("sentiment", ['score', 'magnitude'])
    sentiments = []

    print('Analysing sentiment for {} tweets...'.format(len(tw_texts)))
    for text in tw_texts:
        document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT)
        annotations = client.analyze_sentiment(document=document)

        sentiments.append(sentiment(annotations.document_sentiment.score,
                                    annotations.document_sentiment.magnitude))
        if DEBUG:
            print('\n{:40}'.format(text))
            print_result(annotations)

    print('Done.')
    return sentiments

def print_result(annotations):
    """Presenting the Google sentiment results"""
    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    for index, sentence in enumerate(annotations.sentences):
        sentence_sentiment = sentence.sentiment.score
        print('Sentence {} has a sentiment score of {}'.format(index, sentence_sentiment))

    print('Overall Sentiment: score of {:.2} with magnitude of {:.2}'.format(score, magnitude))
    return 0