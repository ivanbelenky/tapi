from app import crontab, twitter
from playground import (
    save_all_hagovs,
    fetch_and_save_popular_hagovs_recent_tweets,
)


@crontab.job(minute='59', hour='23')
def refresh_hagovs():
    save_all_hagovs(twitter=twitter)


@crontab.job(minute='*/15')
def refresh_relevant_tweets(twitter=twitter):
    fetch_and_save_popular_hagovs_recent_tweets(twitter=twitter)

