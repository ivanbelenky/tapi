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

app = Flask(__name__)

client_id = os.environ.get("TWITTER_CLIENT_ID")
client_secret = os.environ.get("TWITTER_CLIENT_SECRET")

@app.route("/")
def root():
    global twitter
    twitter = TwitterAPI(
        client_id=client_id, 
        client_secret=client_secret, 
        manual_auth_flow=False
    )
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
    

if __name__ == "__main__":
    app.run(ssl_context='adhoc', debug=True)