import os
import time
import json
from typing import List, Union, Dict
from dataclasses import asdict


from dotenv import load_dotenv
from pprint import pprint

from api import TwitterAPI
from constants import ALL_SCOPES, ALL_USER_FIELDS

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



if __name__ == "__main__":
    fetch_and_save_all_followers('747898915', twitter=twitter)
    