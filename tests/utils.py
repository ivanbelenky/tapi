import sys
import os
from pathlib import Path
import pickle
import time

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from api import *
from constants import *

REFRESH_MARGIN = 60

def create_and_save_api():
    twitter = TwitterAPI(
            os.environ.get('TWITTER_CLIENT_ID'),
            os.environ.get('TWITTER_CLIENT_SECRET'),
            manual=True,
            bearer_token=os.environ.get('TWITTER_BEARER_TOKEN'),
            scopes=ALL_SCOPES,
        )
    with open('twitter.api', 'wb') as file:
        pickle.dump(twitter, file)
    return twitter


def auto_refresh(test_function):
    def wrapper(*args, **kwargs):
        twitter = kwargs.get('twitter')
        if twitter.token.get('expires_at') - time.time() < REFRESH_MARGIN:
            print("Token expired, creating new one...")
            twitter = create_and_save_api()
        kwargs['twitter'] = twitter
        return test_function(*args, **kwargs)
    return wrapper



success = False
if 'twitter.api' in os.listdir():
    print("Found tapi session...\n")
    try:
        with open("twitter.api", 'rb') as file:
            twitter = pickle.load(file)
    
        if int(time.time()) > twitter.token.get('expires_at'):
            print("session already expired")
            twitter = create_and_save_api()
        success=True
    except Exception as e:
        print("Failed to retrieve twitter session, creating one...")
        twitter = create_and_save_api() 
else:
    print("did not found session, creating one...\n")
    twitter = create_and_save_api()


