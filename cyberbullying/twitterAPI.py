import os
import tweepy
import pandas as pd
pd.set_option('display.max_colwidth', 100)

# Twitter API Credentials
CONSUMER_KEY = os.environ.get("TWITTER_API_CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("TWITTER_API_CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("TWITTER_API_ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("TWITTER_API_ACCESS_TOKEN_SECRET")

# Authorize Twitter API
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# Call Twitter API
api = tweepy.API(auth, wait_on_rate_limit=True)

# Collect most recent 20 tweets based on keywords
def get_tweets(input_text):
    tweets_list = []
    try:
        tweets = api.search(q=input_text, count=100, lang='en')
        for tweet in tweets[:20]:
            status = api.get_status(tweet.id, tweet_mode="extended")  # Use extended mode
            try:
                tweet_full_text = status.retweeted_status.full_text  # Retweet
            except AttributeError:
                tweet_full_text = status.full_text  # Not a retweet
            tweets_list.append({'tweet_text': tweet_full_text})
        return pd.DataFrame.from_dict(tweets_list)
    except BaseException as e:
        print('failed on_status,', str(e))
        return pd.DataFrame()


# Collect most recent 20 tweets based on Twitter User ID
def userid_search(user_query):
    tweets_list=[]
    try:
        tweets = api.user_timeline(screen_name=user_query, count=100, exclude_replies=True,
                               include_rts =False, tweet_mode='extended')  # Use extended mode
        for tweet in tweets[:20]:
            tweets_list.append({'tweet_text': tweet.full_text})
        return pd.DataFrame.from_dict(tweets_list)

    except BaseException as e:
        print('failed user search,', str(e))
        return pd.DataFrame()
