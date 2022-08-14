import os
import json
import datetime
from typing import Dict, Any
from functools import wraps, partial 
import pytz
import requests 
from dotenv import load_dotenv



from constants import MAX_PAGES
from fetch.users_lookup import UsersLookup
from fetch.users_lookup import (
    get_user_by_id_url,
    get_users_by_id_url,
    get_users_by_username_regex_url,
    get_users_by_usernames_url,
    get_users_followed_lists_by_id_url,
    get_users_list_memberships_by_id_url,
    get_users_owned_lists_by_id_url,
    get_users_pinned_lists_by_id_url,
    get_user_followers_by_id_url,
    get_user_following_by_id_url,
    get_user_liked_tweets_by_id_url,
    get_user_timelines_reverse_chronological_by_id_url,
    get_user_mentions_by_id_url,
    get_blocked_users_by_id_url,
    get_me_url,
    get_users_bookmarks_by_id_url,
    get_muted_users_by_id_url

)

load_dotenv()

BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN", None)
OAUTH_SIGNATURE = os.environ.get("TWITTER_OAUTH_SIGNATURE", None)


def doublewrap(f):
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return f(args[0])
        else:
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec

def paginator(session, url):
    next_url = url
    for page in range(MAX_PAGES):
        if page != 0:
            next_url = UsersLookup.next_page(url, response)
        response = session.get(next_url)
        if response.status_code == 200:
            yield response.json()
        else:
            break

@doublewrap
def GET(method, signature_needed=False, pagination=False):
    def wrapper(self, *args, **kwargs):
        try:
            if signature_needed and self.oauth_signature is None:
                raise AttributeError("OAuth signature not set")
            
            token = self.oauth_signature if signature_needed else self.api_token 
            self.session.headers.update({'Authorization': f"Bearer {token}"})
            
            url = method(self, *args, **kwargs)
            if not pagination:
                res = self.session.get(url)
                res.raise_for_status()
                return res.json()
            else:
                return paginator(self.session, url)            
        except AttributeError as e:
            print(e)
        except Exception as e:
            print(f"Failed to get {method.__name__}: {e}")
            return res
    return wrapper


class TwitterAPI:
    def __init__(self, token=BEARER_TOKEN, signature=OAUTH_SIGNATURE):
        self.api_token = token
        self.oauth_signature = signature
        self.session = requests.session()

    @GET
    def users_by_ids(
        self, 
        users_ids: list, 
        use_default: bool = True, 
        expansions: list = None, 
        user_fields: list = None, 
        tweet_fields: list = None
    ):
        """
            expansions: ['pinned_tweet_id']

        """
        return get_users_by_id_url(
            users_ids, 
            use_default, 
            expansions, 
            user_fields, 
            tweet_fields
        )

    @GET
    def users_by_usernames(
        self, 
        usernames: list, 
        use_default: bool = True, 
        expansions: list = None, 
        user_fields: list = None, 
        tweet_fields: list = None
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        return get_users_by_usernames_url(
            usernames,
            use_default,
            expansions,
            user_fields,
            tweet_fields
        )

    @GET
    def users_by_username_regex(
        self,
        username: str,
        use_default: bool = True,
        expansions: list = None,
        user_fields: list = None,
        tweet_fields: list = None
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        return get_users_by_username_regex_url(
            username,
            use_default,
            expansions,
            user_fields,
            tweet_fields
        )

    @GET
    def user_by_id(
        self,
        user_id: str,
        use_default: bool = True,
        expansions: list = None,
        user_fields: list = None,
        tweet_fields: list = None
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        return get_user_by_id_url(
            user_id,
            use_default,
            expansions,
            user_fields,
            tweet_fields
        )

    @GET
    def users_followed_lists_by_id(
        self,
        user_id: str,
        use_default: bool = True,
        expansions: list = None,
        user_fields: list = None,
        list_fields: list = None,
    ):
        """
            expansions: ['owner_id']
        """

        return get_users_followed_lists_by_id_url(
            user_id,
            use_default,
            expansions,
            user_fields,
            list_fields
        )

    @GET
    def users_list_membership_by_id(
        self,
        user_id: str,
        use_default: bool = True,
        expansions: list = None,
        user_fields: list = None,
        list_fields: list = None,
    ):
        """
            expansions: ['owner_id']
        """

        return get_users_list_memberships_by_id_url(
            user_id,
            use_default,
            expansions,
            user_fields,
            list_fields
        )

    @GET
    def users_owned_lists_by_id(
        self,
        user_id: str,
        use_default: bool = True,
        expansions: list = None,
        user_fields: list = None,
        list_fields: list = None,
    ):
        """
            expansions: ['owner_id']
        """

        return get_users_owned_lists_by_id_url(
            user_id,
            use_default,
            expansions,
            user_fields,
            list_fields
        )

    @GET
    def users_pinned_lists_by_id(
        self,
        user_id: str,
        use_default: bool = True,
        expansions: list = None,
        user_fields: list = None,
        list_fields: list = None,
    ):
        """
            expansions: ['owner_id']
        """

        return get_users_pinned_lists_by_id_url(
            user_id,
            use_default,
            expansions,
            user_fields,
            list_fields
        )

    @GET(pagination=True)
    def user_followers_by_id(
        self,
        user_id: str,
        use_default: bool = True,
        expansions: list = None,
        user_fields: list = None,
        tweet_fields: list = None,
    ):
        """
            expansions: ['pinned_tweet']
        """

        return get_user_followers_by_id_url(
            user_id,
            use_default,
            expansions,
            user_fields,
            tweet_fields
        )

    @GET
    def user_following_by_id(
        self,
        user_id: str,
        use_default: bool = True,
        expansions: list = None,
        user_fields: list = None,
        tweet_fields: list = None,
    ):
        """
            expansions: ['pinned_tweet']
        """

        return get_user_following_by_id_url(
            user_id,
            use_default,
            expansions,
            user_fields,
            tweet_fields
        )

    @GET
    def user_liked_tweets_by_id(
        self,
        user_id: str,
        use_default: bool = True,
        expansions: list = None,
        tweet_fields: list = None,
        media_fields: list = None,
        poll_fields: list = None,
        user_fields: list = None,
        place_fields: list = None,
    ):
        """
            expansions: [
                'attachments',
                'media_keys', 
                'attachments.poll_ids',
                'author_id',
                'entities.mentions.username',
                'geo.place_id',
                'in_reply_to_user_id',
                'referenced_tweets.id',
                'referenced_tweets.id.author_id'
            ]
        """

        return get_user_liked_tweets_by_id_url(
            user_id,
            use_default,
            expansions,
            user_fields,
            tweet_fields,
            media_fields,
            poll_fields,
            user_fields,
            place_fields,
        )
    
    @GET
    def user_mentions_by_id(
        self,
        user_id: str,
        query: Dict[str, Any] = {}, 
        use_default: bool = True,
        expansions: list = None,
        tweet_fields: list = None,
        media_fields: list = None,
        poll_fields: list = None,
        user_fields: list = None,
        place_fields: list = None,
    ):
        """
            query : [
                'since_id',
                'until_id',
                'start_time',
                'end_time',
            ]

            expansions: [
                'attachments.media_keys',
                'attachments.poll_ids',
                'author_id',
                'entities.mentions.username',
                'geo.place_id',
                'in_reply_to_user_id',
                'referenced_tweets.id',
                'referenced_tweets.id.author_id'
            ]
        """

        return get_user_mentions_by_id_url(
            user_id,
            query,
            use_default,
            expansions,
            tweet_fields,
            media_fields,
            poll_fields,
            user_fields,
            place_fields,
        )

    @GET
    def user_timelines_reverse_chronological(
        self,
        user_id: str,
        query: Dict[str, Any] = {},
        use_default: bool = True,
        expansions: list = None,
        tweet_fields: list = None,
        media_fields: list = None,
        poll_fields: list = None,
        user_fields: list = None,
        place_fields: list = None,
    ):
        """
            query : [
                'since_id',
                'until_id',
                'start_time',
                'end_time',
            ]

            expansions: [
                'attachments.media_keys',
                'attachments.poll_ids',
                'author_id',
                'entities.mentions.username',
                'geo.place_id',
                'in_reply_to_user_id',
                'referenced_tweets.id',
                'referenced_tweets.id.author_id'
            ]
        """

        return get_user_timelines_reverse_chronological_by_id_url(
            user_id,
            query,
            use_default,
            expansions,
            tweet_fields,
            media_fields,
            poll_fields,
            user_fields,
            place_fields,
        )

    @GET(signature_needed=True, pagination=True)
    def me(
        self,
        use_default = True,
        expansions: list = None,
        user_fields: list = None,
        tweet_fields: list = None,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        return get_me_url(
            use_default,
            expansions,
            user_fields,
            tweet_fields
        )
    
