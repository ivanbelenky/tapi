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

def fetch_all_hagovs(twitter=twitter):
    hagovs = twitter.get_list_members(
        '1537128547470417925',
        max_results=1000,
        user_fields=ALL_USER_FIELDS,
    )
    with open(f'data/users/hagovs.json', 'w') as file:
        json.dump(
            [asdict(hagov) for hagov in hagovs],
            file,
            skipkeys=True,
            indent=3
        )

def fetch_user_recent_tweets(username: str, twitter=twitter, days_back=7):
    user = twitter.get_users_by_username_regex(username)
    pprint(user)
    qquery = f'from%3A{user.id}'
    tweets = twitter.tweet_recent_search(
        max_results=10,
        start_time=datetime_parser(datetime.utcnow() - timedelta(days=days_back)),
        sort_order='recency',
        qquery=qquery,
        user_fields=[],
        place_fields=[],
        poll_fields=[],
        media_fields=[],
    )
    return tweets

if __name__ == "__main__":
    #fetch_all_hagovs(twitter=twitter)    
    pprint(fetch_user_recent_tweets('tomasrebord', twitter=twitter, days_back=1))