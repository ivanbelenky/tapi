import os
import json

from requests_oauthlib import OAuth2Session
from flask_cors import CORS
from flask_crontab import Crontab
from flask_sslify import SSLify
from flask import (
    Flask, 
    request, 
    redirect,
    jsonify
)
from authlib.integrations.requests_client import OAuth2Session, OAuth2Auth

from api import TwitterAPI
from constants import ALL_SCOPES

app = Flask(__name__)

cors = CORS(app, resources={r"/*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

crontab = Crontab(app)

client_id = os.environ.get("TWITTER_CLIENT_ID")
client_secret = os.environ.get("TWITTER_CLIENT_SECRET")
bearer_token=os.environ.get('TWITTER_BEARER_TOKEN')

global twitter
twitter = TwitterAPI(   
    client_id=client_id, 
    client_secret=client_secret, 
    manual=False,   
    bearer_token=bearer_token,
    scopes=ALL_SCOPES
)

@app.route("/")
def root():
    authorization_url = twitter.create_authorization_url()
    return redirect(authorization_url)


@app.route("/oauth/callback", methods=["GET"])
def callback():
    resp_url = request.base_url + request.full_path
    twitter.fetch_token(resp_url)
    return "You should now have a nice hagovero journey"


@app.route("/refresh", methods=["GET"])
def refresh_token():
    twitter.refresh_token()
    return jsonify(twitter.token)


@app.route('/hagovs', methods=["GET"])
def user_test():
    hagovs = get_hagovs()
    return jsonify(hagovs)


@app.route('/post_tweet', methods=['GET'])
def post_tweet():
    text = request.args.get('text')
    res = twitter.post_tweet(text)
    if res:
        return jsonify(res.json())
    else:
        return {}

@app.route('/relevant_tweets', methods=['GET'])
def relevant_tweets():
    try:
        max_results = int(request.args.get('max_results'))
        max_results = max_results if max_results < 1000 else 1000
    except Exception as e:
        max_results = 1000
    relevant_tweets = get_relevant_tweets(max_results)
    
    return jsonify(relevant_tweets)


def get_relevant_tweets(max_results: int):
    with open('data/tweets/all_relevant_tweets.json', 'r') as file:
        relevant_tweets = json.load(file)
    relevant_tweets = sorted(
        relevant_tweets, 
        key=lambda t: t['public_metrics']['retweet_count']*10 + t['public_metrics']['like_count'], 
        reverse=True
        )[:max_results]
    print(len(relevant_tweets))
    return relevant_tweets


def get_hagovs():
    with open('data/users/hagovs.json', 'r') as file:
        hagovs = json.load(file)
    hagovs = [{k:v for k,v in hagov.items() if k in ['id', 'username', 'profile_image_url', 'public_metrics']} for hagov in hagovs]
    hagovs = sorted(hagovs, key=lambda h: h['public_metrics']['followers_count'], reverse=True)
    return hagovs
    

from playground import (
    save_all_hagovs,
    fetch_and_save_popular_hagovs_recent_tweets,
)


@crontab.job(minute='59', hour='23')
def refresh_hagovs():
    print("refreshing hagovs")
    save_all_hagovs(twitter=twitter)


@crontab.job(minute='*/10')
def refresh_relevant_tweets(twitter=twitter):
    print("refreshing relevant tweets")
    fetch_and_save_popular_hagovs_recent_tweets(twitter=twitter)




if __name__ == "__main__":
    app.run(ssl_context='adhoc', debug=True)

