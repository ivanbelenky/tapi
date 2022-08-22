#!/usr/bin/env python3

import os
from utils import *

def test_oauth_flow():
    client_id = os.environ.get('TWITTER_CLIENT_ID')
    client_secret = os.environ.get('TWITTER_CLIENT_SECRET')
    twitter = TwitterAPI(client_id, client_secret, manual=True)
    print(f"\n\n{twitter.token}")
    
if __name__ == "__main__":
    test_oauth_flow()