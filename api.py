#!/usr/bin/env python3

import os
import base64
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from requests import request

from pprint import pprint
from dotenv import load_dotenv
from authlib.integrations.requests_client import OAuth2Session, OAuth2Auth

import constants
from fetch.lookup import UsersLookup, TweetLookup

load_dotenv()

def paginator(tapi, lookup, max_results):
    url = lookup.create_url()
    next_url = url
    for page in range(max_results//constants.MAX_RESULTS_PER_PAGE+1):
        if page != 0:
            next_url = lookup.next_page(url, response)
        if not next_url:
            break

        response = tapi._get(next_url)
        response.raise_for_status()
        yield response.json()
        
            
def paginate_response(session, lookup, pages):    
    responses = [res for res in paginator(session, lookup, pages)]
    return lookup.paginate_responses(responses)


def doublewrap(f):
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return f(args[0])
        else:
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec


@doublewrap
def GET(method, pagination=False):
    def wrapper(self, *args, **kwargs):
        res = None
        try:
            lookup = method(self, *args, **kwargs)
            if not pagination:
                res = self._get(lookup.create_url())
                res.raise_for_status()
                res = res.json()
            else:
                res = paginate_response(
                    self, 
                    lookup, 
                    kwargs.get('max_results'))
            
            if kwargs.get('save', False):
                lookup.save_response(res)

            return res
        except AttributeError as e:
            print(e)
            return res
        except Exception as e:
            print(f"Failed to get {method.__name__}: {e}")
            return res
    return wrapper


class TwitterAPI:
    def __init__(
        self, 
        client_id, 
        client_secret,
        manual = True, 
        scopes=constants.DEFAULT_SCOPES
    ):
        self.scopes = scopes 
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = self.init_session()
        self.manual = manual
        
        if manual:
            self.manual_auth_flow()
    

    def init_session(self):
        session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scopes,
            redirect_uri=constants.DEFAULT_CALLBACK_URI,
            code_challenge_method="S256",
        )
        return session
    
    def create_authorization_url(self):
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
        code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)  
        authorization_url, _ = self.session.create_authorization_url(
            url=constants.BASE_OAUTH2_AUTHORIZE_URL,
            code_verifier=code_verifier
        )
        self.code_verifier = code_verifier
        return authorization_url

    def fetch_token(self, resp_url):
        self.resp_url = resp_url
        token = self.session.fetch_token(
            url=constants.BASE_OAUTH2_ACCESS_TOKEN_URL,
            authorization_response=self.resp_url,
            code_verifier=self.code_verifier,
        )
        self.token = token

    def refresh_token(self):
        self.session.refresh_token(
            constants.BASE_OAUTH2_ACCESS_TOKEN_URL, 
            refresh_token=self.token['refresh_token']
        )
    
    def manual_auth_flow(self):
        if self.manual:
            authorization_url = self.create_authorization_url()
            print(f"Authorize the api and copy the response:\n {'-'*39}\n {authorization_url}\n")
            resp_url = input("Paste the response from the above link: \n")
            self.fetch_token(resp_url)

    def _get(self, url):
        return request(
            method="GET",
            url=url,
            headers={'Authorization': f"Bearer {self.token['access_token']}"}
        )

    @GET
    def get_users(
        self, 
        users_ids: list,  
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION, 
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS, 
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: bool = False
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        endpoint = constants.USERS_LOOKUP_BY_ID_ENDPOINT
        query = {'ids': users_ids}
        users_lookup = UsersLookup(
            endpoint=endpoint,
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup
        
    @GET
    def get_users_by_usernames(
        self, 
        usernames: list, 
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION, 
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS, 
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: bool = False,
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        endpoint = constants.USERS_LOOKUP_BY_USERNAME_ENDPOINT
        query = {'usernames': usernames}
        users_lookup = UsersLookup(
            endpoint=endpoint,
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup

    @GET
    def get_users_by_username_regex(
        self,
        username: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        endpoint = constants.USERS_LOOKUP_BY_USERNAME_REGEX_ENDPOINT
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<username>', username),
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup

    @GET
    def get_single_user(
        self,
        user_id: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        endpoint = constants.USERS_LOOKUP_BY_USERNAME_ID_ENDPOINT
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup

    @GET(pagination=True)
    def get_user_followed_lists(
        self,
        user_id: str,
        max_results: Optional[int] = constants.MAX_RESULTS_PER_PAGE,
        expansions: Optional[List[str]] = constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        list_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    ):
        """
            expansions: ['owner_id']
        """
        max_results = max_results if max_results < constants.MAX_RESULTS_PER_PAGE else constants.MAX_RESULTS_PER_PAGE
        endpoint = constants.USERS_LOOKUP_FOLLOWED_LISTS_BY_ID_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            list_fields=list_fields
        )
        return users_lookup

    @GET(pagination=True)
    def get_user_list_membership(
        self,
        user_id: str,
        max_results: Optional[int] = constants.MAX_RESULTS_PER_PAGE,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        list_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    ):
        """
            expansions: ['owner_id']
        """
        max_results = max_results if max_results < constants.MAX_RESULTS_PER_PAGE else constants.MAX_RESULTS_PER_PAGE
        endpoint = constants.USERS_LOOKUP_LIST_MEMBERSHIPS_BY_ID_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            list_fields=list_fields
        )
        return users_lookup

    @GET(pagination=True)
    def get_users_owned_lists(
        self,
        user_id: str,
        max_results: Optional[int] = constants.MAX_RESULTS_PER_PAGE,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        list_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    ):
        """
            expansions: ['owner_id']
        """
        max_results = max_results if max_results < constants.MAX_RESULTS_PER_PAGE else constants.MAX_RESULTS_PER_PAGE
        endpoint = constants.USERS_LOOKUP_OWNED_LISTS_BY_ID_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            list_fields=list_fields
        )
        return users_lookup

    @GET
    def get_users_pinned_lists(
        self,
        user_id: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        list_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    ):
        """
            expansions: ['owner_id']
        """
        endpoint = constants.USERS_LOOKUP_PINNED_LISTS_BY_ID_ENDPOINT
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            expansions=expansions,
            user_fields=user_fields,
            list_fields=list_fields
        )
        return users_lookup

    @GET(pagination=True)
    def get_user_followers(
        self,
        user_id: str,
        max_results: Optional[int] = constants.MAX_RESULTS_PER_PAGE,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    ):
        """
            expansions: ['pinned_tweet']
        """
        max_results = max_results if max_results < constants.MAX_RESULTS_PER_PAGE else constants.MAX_RESULTS_PER_PAGE
        endpoint = constants.USERS_LOOKUP_FOLLOWERS_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup

    @GET(pagination=True)
    def get_user_following(
        self,
        user_id: str,
        max_results: Optional[int] = constants.MAX_RESULTS_PER_PAGE,
        expansions: Optional[List[str]] = constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]] = constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]] = constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    ):
        """
            expansions: ['pinned_tweet']
        """
        max_results = max_results if max_results < constants.MAX_RESULTS_PER_PAGE else constants.MAX_RESULTS_PER_PAGE
        endpoint = constants.USERS_LOOKUP_FOLLOWING_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup

    @GET(pagination=True)
    def get_user_liked_tweets(
        self,
        user_id: str,
        max_results: Optional[int] = constants.MAX_RESULTS_PER_PAGE,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        place_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: bool = False,
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
        max_results = max_results if 5 < max_results < constants.MAX_RESULTS_PER_PAGE else constants.MAX_RESULTS_PER_PAGE
        endpoint = constants.USERS_LOOKUP_LIKED_TWEETS_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            user_fields=user_fields,
            place_fields=place_fields            
        )
        return users_lookup
    
    @GET(pagination=True)
    def get_users_that_liked_tweet(
        self,
        tweet_id: str,
        max_results: Optional[int] = constants.MAX_RESULTS_PER_PAGE,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        save: bool = False,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        max_results = max_results if max_results < constants.MAX_RESULTS_PER_PAGE else constants.MAX_RESULTS_PER_PAGE
        endpoint = constants.USERS_LOOKUP_THAT_LIKED_TWEET_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<tweet_id>', tweet_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
        )
        return users_lookup

    @GET
    def get_user_mentions(
        self,
        user_id: str,
        max_results: Optional[int] = constants.MAX_RESULTS_PER_PAGE,
        query: Optional[Dict[str, str]] = {}, 
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        place_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
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
        max_results = max_results if max_results < constants.MAX_RESULTS_PER_PAGE else constants.MAX_RESULTS_PER_PAGE
        endpoint = constants.USERS_LOOKUP_MENTIONS_BY_ID_ENDPOINT
        query['max_results'] = [str(max_results)]
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            user_fields=user_fields,
            place_fields=place_fields            
        )
        return users_lookup

    @GET
    def user_timelines_reverse_chronological(
        self,
        user_id: str,
        query: Dict[str, Any] = {},
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        place_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
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
        endpoint = constants.USERS_LOOKUP_TIMELINES_REVERSE_CHRONOLOGICAL_BY_ID_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            user_fields=user_fields,
            place_fields=place_fields            
        )
        return users_lookup

    @GET
    def me(
        self,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: bool = True,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        endpoint = constants.USERS_LOOKUP_ME_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        users_lookup = UsersLookup(
            endpoint=endpoint,
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup

    @GET(pagination=True)    
    def blocked_users(
        self,
        user_id: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: bool = True,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        endpoint = constants.USERS_LOOKUP_BLOCKED_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup
        
    @GET(pagination=True)
    def users_bookmarks_by_id_url(
        self,
        user_id: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: bool = True,
    ):
        """
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
        endpoint = constants.USERS_LOOKUP_BOOKMARKS_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            place_fields=place_fields
        )
        return users_lookup

    @GET(pagination=True)
    def user_muted(
        self,
        user_id: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: bool = True,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        endpoint = constants.USERS_LOOKUP_MUTED_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup
    
    @GET(pagination=True)
    def users_that_retweeted(
        self,
        tweet_id: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: bool = True,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        endpoint = constants.USERS_LOOKUP_BY_RETWEET_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', tweet_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup
    
    @GET(pagination=True)
    def users_tweets(
        self,
        user_ids: list,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: bool = True,
    ):
        """
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
        endpoint = constants.TWEETS_LOOKUP_BY_USERS_ENDPOINT
        query = {
            'ids': user_ids,
            'max_results': [constants.MAX_RESULTS_PER_PAGE]
        }
        tweet_lookup = TweetLookup(
            endpoint=endpoint,
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            place_fields=place_fields
        )
        return tweet_lookup

    @GET
    def tweet(
        self,
        tweet_id: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: bool = True,
    ):
        """
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
        endpoint = constants.TWEETS_LOOKUP_BY_ID_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        tweet_lookup = TweetLookup(
            endpoint=endpoint.replace('<id>', tweet_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            place_fields=place_fields
        )
        return tweet_lookup

    @GET(pagination=True)
    def tweet_quotes(
        self,
        tweet_id: str,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: bool = True,
    ):
        """
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
        endpoint = constants.TWEETS_LOOKUP_TWEETS_QUOTES_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        tweet_lookup = TweetLookup(
            endpoint=endpoint.replace('<id>', tweet_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            place_fields=place_fields
        )
        return tweet_lookup

    @GET(pagination=True)
    def tweet_full_search(
        self,
        recent: bool = False,
        start_time: datetime = None,
        end_time: datetime = None,
        since_id: str = None,
        until_id: str = None,
        sort_order: str = 'recency',
        qquery: str = None,
        expansions: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= constants.DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
    ):

        """
        :param start_time: Oldest UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param end_time: Newest UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param since_id: Greater than tweet id for response. Exclude this since_id.
        :param until_id: Less than tweet id for response. Exclude this until_id.
        :param sort_order: Sort by 'recency' or 'relevancy'
        :param qquery: build query with https://developer.twitter.com/apitools/api?endpoint=%2F2%2Ftweets%2Fsearch%2Fall&method=get"
        """

        endpoint = constants.TWEETS_LOOKUP_FULL_SEARCH_ENDPOINT if recent else constants.TWEETS_LOOKUP_FULL_SEARCH_ENDPOINT 
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        if qquery:
            query['query'] = qquery
        if start_time:
            query['start_time'] = start_time
        if end_time:
            query['end_time'] = end_time
        if since_id:
            query['since_id'] = since_id
        if until_id:
            query['until_id'] = until_id
        if sort_order in ['recency', 'relevancy']:
            until_id['sort_order'] = sort_order
        
        tweet_lookup = TweetLookup(
            endpoint=endpoint,
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            place_fields=place_fields
        )
        return tweet_lookup


    @GET(pagination=True)
    def tweet_counts(
        self,
        recent: bool = False,
        start_time: datetime = None,
        end_time: datetime = None,
        since_id: str = None,
        until_id: str = None,
        granularity: str = 'day',
        qquery: str = None,
        count_fields = constants.DEFAULT_TWEETS_LOOKUP_COUNT,
    ):

        endpoint = constants.TWEETS_LOOKUP_RECENT_COUNT_ENDPOINT if recent else constants.TWEETS_LOOKUP_ALL_COUNT_ENDPOINT
        query = {'max_results': [constants.MAX_RESULTS_PER_PAGE]}
        if qquery:
            query['query'] = qquery
        if start_time:
            query['start_time'] = start_time
        if end_time:
            query['end_time'] = end_time
        if since_id:
            query['since_id'] = since_id
        if until_id:
            query['until_id'] = until_id
        if granularity in ["minute", 'hour', 'day']:
            query['granularity'] = granularity

        tweet_lookup = TweetLookup(
            endpoint=endpoint,
            query=query,
            count_fields=count_fields,
        )
        return tweet_lookup

    


        


