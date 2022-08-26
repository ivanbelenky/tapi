import os

from requests_oauthlib import OAuth2Session
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

client_id = os.environ.get("TWITTER_CLIENT_ID")
client_secret = os.environ.get("TWITTER_CLIENT_SECRET")
global twitter
twitter = TwitterAPI(
    client_id=client_id, 
    client_secret=client_secret, 
    manual=False,
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


@app.route('/users_test', methods=["GET"])
def user_test():
    res = twitter.get_user_followers(
        user_id='747898915',
        max_results=6,
    )
    print(res)
    return jsonify(res)


@app.route('/post_tweet', methods=['GET'])
def post_tweet():
    text = request.args.get('text')
    res = twitter.post_tweet(text)
    if res:
        return jsonify(res.json())
    else:
        return {}


if __name__ == "__main__":
    app.run(ssl_context='adhoc', debug=True)