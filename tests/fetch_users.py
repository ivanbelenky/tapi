import time
from pprint import pprint
from utils import twitter, auto_refresh

import constants

@auto_refresh
def test_get_users_by_ids(twitter=twitter):
    return twitter.get_users(users_ids=['747898915'])

@auto_refresh
def test_get_users_by_ids_expansions(twitter=twitter):
    return twitter.get_users(
        users_ids=['747898915'],
        expansions=['pinned_tweet_id'], 
        tweet_fields=['public_metrics'],
        user_fields=constants.DEFAULT_USERS_LOOKUP_USER_FIELDS+['public_metrics', 'withheld']
    )

@auto_refresh
def test_get_users_by_usernames(twitter=twitter):
    return twitter.get_users_by_usernames(usernames=['tomasrebord'])


@auto_refresh
def test_get_users_by_username_regex(twitter=twitter):
    return twitter.get_users_by_username_regex(username='tomasrebord')


@auto_refresh
def test_get_single_user(twitter=twitter):
    return twitter.get_single_user(user_id='747898915')


@auto_refresh
def test_get_user_followed_lists(twitter=twitter):
    return twitter.get_user_followed_lists(
        user_id='747898915',
        max_results=4,
        expansions=['owner_id']
    )


@auto_refresh
def test_get_user_list_membership(twitter=twitter):
    return twitter.get_user_list_membership(
        user_id='747898915',
        max_results=99,
        expansions=['owner_id']
    )


@auto_refresh
def test_get_users_owned_lists(twitter=twitter):
    return twitter.get_users_owned_lists(
        user_id='747898915',
        max_results=13,
        expansions=['owner_id']
    )


@auto_refresh
def test_get_users_pinned_lists(twitter=twitter):
    return twitter.get_users_pinned_lists(
        user_id='747898915',
        expansions=['owner_id']
    )


@auto_refresh
def test_get_user_followers(twitter=twitter):
    return twitter.get_user_followers(
        user_id='747898915',
        max_results=2,
    )


@auto_refresh
def test_get_user_following(twitter=twitter):
    return twitter.get_user_following(
        user_id='747898915',
        max_results=2,
    )


@auto_refresh
def test_get_user_liked_tweets(twitter=twitter):
    return twitter.get_user_liked_tweets(
        user_id='747898915',
        max_results=2,
    )


@auto_refresh
def test_get_users_that_liked_tweet(twitter=twitter):
    return twitter.get_users_that_liked_tweet(
        tweet_id='1560762974318518273',
        max_results=4,
    )


@auto_refresh
def test_get_users_that_liked_tweet(twitter=twitter):
    return twitter.get_users_that_liked_tweet(
        user_id='747898915',
        max_results=4,
    )




if __name__ == "__main__":
    #pprint(test_get_users_by_ids(twitter=twitter))
    #pprint(test_get_users_by_ids_expansions(twitter=twitter))
    #pprint(test_get_users_by_usernames(twitter=twitter))
    #pprint(test_get_users_by_username_regex(twitter=twitter))
    #pprint(test_get_single_user(twitter=twitter))
    #pprint(test_get_user_followed_lists(twitter=twitter))
    #pprint(test_get_user_list_membership(twitter=twitter))
    #pprint(test_get_users_owned_lists(twitter=twitter))
    #pprint(test_get_users_pinned_lists(twitter=twitter))
    #pprint(test_get_user_followers(twitter=twitter))
    #pprint(test_get_user_following(twitter=twitter))
    #pprint(test_get_user_liked_tweets(twitter=twitter))
    #pprint(test_get_users_that_liked_tweet(twitter=twitter))
    pprint(test_get_users_that_liked_tweet(twitter=twitter))
    