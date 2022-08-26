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
        max_results=4,
        expansions=['owner_id']
    )


@auto_refresh
def test_get_users_owned_lists(twitter=twitter):
    return twitter.get_users_owned_lists(
        user_id='747898915',
        max_results=3,
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
def test_get_user_mentions(twitter=twitter):
    return twitter.get_user_mentions(
        user_id='747898915',
        max_results=5,
    )

@auto_refresh
def test_get_user_timelines_reverse_chronological(twitter=twitter):
    return twitter.get_user_timelines_reverse_chronological(
        user_id='1557912497277095938',
        max_results=5,
    )


@auto_refresh
def test_get_me(twitter=twitter):
    return twitter.get_me()


@auto_refresh
def test_get_blocked_users(twitter=twitter):
    return twitter.get_blocked_users(
        user_id='1557912497277095938',
        max_results=5,
    )


@auto_refresh
def test_get_muted_users(twitter=twitter):
    return twitter.get_users_muted(
        user_id='1557912497277095938',
        max_results=5,
    )

@auto_refresh
def test_get_users_that_retweeted(twitter=twitter):
    return twitter.get_users_that_retweeted(
        tweet_id='1562209127820050432',
        max_results=5,
    )

@auto_refresh
def test_post_tweet(twitter=twitter):
    return twitter.post_tweet(
        text='second test'
    )




if __name__ == "__main__":
    #pprint(test_get_users_by_ids(twitter=twitter))
    print('\n')
    #pprint(test_get_users_by_ids_expansions(twitter=twitter))
    print('\n')
    #pprint(test_get_users_by_usernames(twitter=twitter))
    print('\n')
    #pprint(test_get_users_by_username_regex(twitter=twitter))
    print('\n')
    #pprint(test_get_single_user(twitter=twitter))
    print('\n')
    #pprint(test_get_user_followed_lists(twitter=twitter))
    print('\n')
    #pprint(test_get_user_list_membership(twitter=twitter))
    print('\n')
    #pprint(test_get_users_owned_lists(twitter=twitter))
    print('\n')
    #pprint(test_get_users_pinned_lists(twitter=twitter))
    print('\n')
    #pprint(test_get_user_followers(twitter=twitter))
    print('\n')
    #pprint(test_get_user_following(twitter=twitter))
    print('\n')
    #pprint(test_get_user_liked_tweets(twitter=twitter))
    print('\n')
    #pprint(test_get_users_that_liked_tweet(twitter=twitter))
    print('\n')
    #pprint(test_get_user_mentions(twitter=twitter))
    print('\n')
    #pprint(test_get_user_timelines_reverse_chronological(twitter=twitter))
    print('\n')
    #pprint(test_get_me(twitter=twitter))
    print('\n')
    #pprint(test_get_blocked_users(twitter=twitter))
    print('\n')
    #pprint(test_get_muted_users(twitter=twitter))
    print('\n')
    #pprint(test_get_users_that_retweeted(twitter=twitter))
    pprint(test_post_tweet(twitter=twitter))