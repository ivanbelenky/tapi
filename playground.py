from concurrent.futures import ThreadPoolExecutor
from multiprocessing.pool import ThreadPool
import os
import time
import json
from tkinter.tix import Tree
from typing import List, Union, Dict
from dataclasses import asdict
from datetime import datetime, timedelta

from dotenv import load_dotenv
from pprint import pprint

from api import TwitterAPI
from constants import ALL_SCOPES, ALL_TWEET_FIELDS, ALL_USER_FIELDS
from utils import datetime_parser

load_dotenv()

twitter = TwitterAPI(
    os.environ.get('TWITTER_CLIENT_ID'),
    os.environ.get('TWITTER_CLIENT_SECRET'),
    manual=True,
    bearer_token=os.environ.get('TWITTER_BEARER_TOKEN'),
    scopes=ALL_SCOPES,
)

def fetch_public_metrics_user(user_id: str, twitter=twitter):
    return twitter.get_single_user(
        user_id,
        user_fields=['public_metrics']
    )

def fetch_and_save_all_followers(user_id: str, twitter=twitter):
    user_followers = []
    try:
        user = fetch_public_metrics_user(user_id, twitter=twitter)
        user_followers_count = user.public_metrics.followers_count
        user_followers = twitter.get_user_followers(
            user_id,
            max_results=user_followers_count,
            user_fields=ALL_USER_FIELDS,
        )
        with open(f'data/users/user_{user_id}_followers_{time.time()}.json', 'w') as file:
            json.dump(
                [asdict(uf) for uf in user_followers], 
                file, 
                skipkeys=True,
                indent=3
            )
    except Exception as e:
        print(f"Failed to fetch all followers: {e}")

    return user_followers  

def fetch_user_recent_tweets(username: str, twitter=twitter, days_ago=7, since_id=None):
    user = twitter.get_users_by_username_regex(username)
    if user:
        qquery = f'from%3A{user.id}'

        tweets = twitter.tweet_recent_search(
            max_results=10,
            start_time=datetime_parser(datetime.utcnow() - timedelta(days=days_ago)),
            sort_order='recency',
            qquery=qquery,
            user_fields=[],
            place_fields=[],
            poll_fields=[],
            media_fields=[],
        )
        return tweets


def save_all_hagovs(twitter=twitter):
    hagovs = twitter.get_list_members(
        '1537128547470417925',
        max_results=1000,
        user_fields=ALL_USER_FIELDS,
    )
    print(f"Fetched all hagovs {len(hagovs) if hagovs else 0}")
    with open(f'data/users/hagovs.json', 'w') as file:
        json.dump(
            [asdict(hagov) for hagov in hagovs],
            file,
            skipkeys=True,
            indent=3
        )

def fetch_and_save_popular_hagovs_recent_tweets(twitter=twitter):
    try: 
        with open('data/users/hagovs.json', 'r') as file:
            print("Loading hagovs from file")
            hagovs = json.load(file)
    except Exception as e:
        print("Failed to load hagovs from file, fetching them")
        save_all_hagovs(twitter=twitter)
        with open('data/users/hagovs.json', 'r') as file:
            hagovs = json.load(file)

    popular_hagovs = sorted(hagovs, key=lambda h: h['public_metrics']['followers_count'], reverse=True)[:50]
    print(f"Fetching recent tweets for {[pop['username'] for pop in popular_hagovs]}")
    popular_hagovs_ids = [hagov['id'] for hagov in popular_hagovs]
    
    relevant_tweets = []
    last_hagov_tweet = {}

    if 'all_relevant_tweets.json' in os.listdir('data/tweets/'):
        print("Found relevant tweets file")
        with open('data/tweets/all_relevant_tweets.json', 'r') as file:
            relevant_tweets = json.load(file)

        for tweet in relevant_tweets:
            if not last_hagov_tweet.get(tweet['author_id']):
                last_hagov_tweet[tweet['author_id']] = tweet 
            if int(last_hagov_tweet[tweet['author_id']]['id']) < int(tweet['id']):
                last_hagov_tweet[tweet['author_id']] = tweet
        
    fetched_tweets = []
    start_time_dt = datetime_parser(datetime.utcnow() - timedelta(days=6))
    
    with ThreadPoolExecutor() as executor:
        results = []
        for hagov in popular_hagovs_ids:
           results.append(executor.submit(fetch_recent_task, last_hagov_tweet, hagov, start_time_dt, twitter=twitter))

    for result in results:
        if result.result():
            fetched_tweets.extend([asdict(res) for res in result.result()])

    relevant_tweets.extend(fetched_tweets)
    with open('data/tweets/all_relevant_tweets.json', 'w') as file:
        print("Saving relevant tweets...")
        json.dump(relevant_tweets, file, skipkeys=True, indent=3)
    
    return True

def fetch_recent_task(last_hagov_tweet, hagov, start_time, twitter=twitter):
    qquery = f'from%3A{hagov}%20-is%3Aretweet'
    since_id = last_hagov_tweet.get(hagov, {}).get('id', None)
    tweets = twitter.tweet_recent_search(
        max_results=100,
        start_time=None if since_id else start_time,
        since_id=since_id if since_id else None,
        sort_order='recency',
        qquery=qquery,
        user_fields=[],
        place_fields=[],
        poll_fields=[],
        media_fields=[],
    )
    print(f"Fetched {0 if not tweets else len(tweets)} tweets from {hagov}")

    return tweets


    

if __name__ == "__main__":
    #save_all_hagovs(twitter=twitter)
    #pprint(fetch_user_recent_tweets('tomasrebord', twitter=twitter, days_ago=1))
    #pprint(save_all_hagovs(twitter=twitter))
    fetch_and_save_popular_hagovs_recent_tweets(twitter=twitter)