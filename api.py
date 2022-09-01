#!/usr/bin/env python3

from inspect import Attribute
from multiprocessing.sharedctypes import Value
import os
import base64
import json
import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from requests import request
import time

from pprint import pprint
from dotenv import load_dotenv
from authlib.integrations.requests_client import OAuth2Session, OAuth2Auth

from constants import *
from limiter import LIMITER
from lookup import UsersLookup, TweetLookup

load_dotenv()

def paginator(tapi, lookup, max_results, limit, app_only_auth):
    url = lookup.create_url()
    next_url = url
    n_pages = max_results//MAX_RESULTS_PER_PAGE_DEFAULT+1
    for page in range(n_pages):
        time.sleep(limit)
        print(f"Fetched page {page+1} of {n_pages}")
        if page != 0:
            next_url = lookup.next_page(url, response)
        if not next_url:
            break

        response = tapi._get(next_url, app_only_auth)
        response.raise_for_status()
        yield response.json()
        
            
def paginate_response(session, lookup, max_results, limit, app_only_auth):    
    responses = [res for res in paginator(session, lookup, max_results, limit, app_only_auth)]
    return lookup.paginate_responses(responses)


def doublewrap(f):
    def new_dec(*args, **kwargs):
        if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
            return f(args[0])
        else:
            return lambda realf: f(realf, *args, **kwargs)

    return new_dec


@doublewrap
def GET(method, pagination=False, app_only_auth=False):
    def wrapper(self, *args, **kwargs):
        res = None
        try:
            lookup = method(self, *args, **kwargs)
            
            if not pagination:
                res = self._get(lookup.create_url(), app_only_auth)
                res.raise_for_status()
                res = res.json() if res.json().get('data') else {}
            else:
                res = paginate_response(
                    self, 
                    lookup, 
                    kwargs.get('max_results'),
                    15*60//LIMITER[method.__name__]['limit'],
                    app_only_auth
                )
            
            if kwargs.get('save', False):
                lookup.save_response(res)

            return lookup.datify(res)
        except AttributeError as e:
            print(e)
            return res
        except Exception as e:
            print(f"Failed to get {method.__name__}: {type(e)} {e}")
            try:
                print(res.json().get('errors'),'\n')
            except Exception as e:
                pass
            return res
    return wrapper

def POST(method):
    def wrapper(self, *args, **kwargs):
        res = None
        try:
            url, payload = method(self, *args, **kwargs)
            res = self._post(url, payload)
            res.raise_for_status() 
        except Exception as e:
            try:
                pprint(res.json())
            except:
                pass
            print(f"Failed to post tweet due to {e}")        
        return res
    return wrapper



class TwitterAPI:
    def __init__(
        self, 
        client_id: str, 
        client_secret: str,
        manual: Optional[bool] = True,
        bearer_token: Optional[str] = None,
        scopes: Optional[List[str]] = DEFAULT_SCOPES
    ):
        self.scopes = scopes 
        self.client_id = client_id
        self.client_secret = client_secret
        self.session = self.init_session()
        self.bearer_token = bearer_token
        self.manual = manual
        self.token = self.retrieve_token()

        if manual and self._should_auth():
            self.manual_auth_flow()
        
        if self._should_refresh():
            self.refresh_token()

    def init_session(self) -> OAuth2Session:
        session = OAuth2Session(
            client_id=self.client_id,
            client_secret=self.client_secret,
            scope=self.scopes,
            redirect_uri=DEFAULT_CALLBACK_URI,
            code_challenge_method="S256",
        )
        return session
    
    def create_authorization_url(self) -> str:
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
        code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)  
        authorization_url, _ = self.session.create_authorization_url(
            url=BASE_OAUTH2_AUTHORIZE_URL,
            code_verifier=code_verifier
        )
        self.code_verifier = code_verifier
        return authorization_url

    def fetch_token(self, resp_url) -> None:
        self.resp_url = resp_url
        token = self.session.fetch_token(
            url=BASE_OAUTH2_ACCESS_TOKEN_URL,
            authorization_response=self.resp_url,
            code_verifier=self.code_verifier,
        )
        self.token = token
        self.save_token()

    def refresh_token(self) -> None:
        try:
            self.token = self.session.refresh_token(
                BASE_OAUTH2_ACCESS_TOKEN_URL, 
                refresh_token=self.token['refresh_token']
            )
        except Exception as e:
            basic_token = base64.b64encode(f'{self.client_id}:{self.client_secret}'.encode('utf-8')).decode('utf-8')
            res = request(
                method='POST',
                url=BASE_OAUTH2_ACCESS_TOKEN_URL,
                data={
                    'refresh_token': self.token['refresh_token'],
                    'grant_type': 'refresh_token',
                    'client_id': self.client_id
                },
                headers={
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Authorization': f'Basic {basic_token}'
                }
            )
            refresh_token = res.json()
            self.token['access_token'] = refresh_token['access_token']
            self.token['refresh_token'] = refresh_token['refresh_token']
            self.token['expires_at'] = int(time.time()) + refresh_token['expires_in']
        
        self.save_token()            

    def retrieve_token(self):
        try:
            if 'twitter.token' in os.listdir('data/saved_tokens'):
                with open('data/saved_tokens/twitter.token', 'r') as file:
                    return json.load(file)
            else:
                return None
        except Exception as e:
            print(f"Failed to retrieve token: {e}") 


    def save_token(self):
        try:
            if self.token:
                with open('data/saved_tokens/twitter.token', 'w') as file:
                    json.dump(self.token, file)
        except Exception as e:
            print(f"Failed to save token: {e}")

    def _should_refresh(self):
        if self.token:
            if int(time.time()) - REFRESH_MARGIN > self.token['expires_at']:
                return True
            return False
    
    def _should_auth(self):
        if not self.token:
            return True
        elif self.token['expires_at'] + REFRESH_REFRESH_MARGIN < int(time.time()):
            return True
        else:
            return False

    def manual_auth_flow(self):
        if self.manual:
            authorization_url = self.create_authorization_url()
            print(f"Authorize the api and copy the response:\n {'-'*39}\n {authorization_url}\n")
            resp_url = input("Paste the response from the above link: \n")
            self.fetch_token(resp_url)

    def _get(self, url, app_only_auth):
        if self._should_refresh():
            self.refresh_token()
        token = self.token['access_token'] if not app_only_auth else self.bearer_token
        if token:
            return request(
                method="GET",
                url=url,
                headers={
                    'Authorization': f"Bearer {token}"
                }
            )
        raise ValueError("No Bearer Token found.")
    
    def _post(self, url, payload):
        if self._should_refresh():
            self.refresh_token()
        return request(
            method='POST',
            url=url,
            json=payload,
            headers={
                'Authorization': f'Bearer {self.token["access_token"]}',
                'Content-type': 'application/json'
            }
        )

    @GET
    def get_users(
        self, 
        users_ids: List[str],  
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION, 
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS, 
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: Optional[bool] = False
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        if len(users_ids) > MAX_USERS_ID:
            raise AttributeError("User ids must not exceed 100")

        endpoint = USERS_LOOKUP_BY_ID_ENDPOINT
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
        usernames: List[str], 
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION, 
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS, 
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: Optional[bool] = False,
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        endpoint = USERS_LOOKUP_BY_USERNAME_ENDPOINT
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
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        endpoint = USERS_LOOKUP_BY_USERNAME_REGEX_ENDPOINT
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
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    ):
        """
            expansions: ['pinned_tweet_id'] 
        """
        endpoint = USERS_LOOKUP_BY_USERNAME_ID_ENDPOINT
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
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]] = DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        list_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    ):
        """
            expansions: ['owner_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_FOLLOWED_LISTS_BY_ID_ENDPOINT
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
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        list_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    ):
        """
            expansions: ['owner_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_LIST_MEMBERSHIPS_BY_ID_ENDPOINT
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
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        list_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    ):
        """
            expansions: ['owner_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_OWNED_LISTS_BY_ID_ENDPOINT
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
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        list_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    ):
        """
            expansions: ['owner_id']
        """
        endpoint = USERS_LOOKUP_PINNED_LISTS_BY_ID_ENDPOINT
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
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_USER,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    ):
        """
            expansions: ['pinned_tweet']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_USER else MAX_RESULTS_PER_PAGE_USER
        endpoint = USERS_LOOKUP_FOLLOWERS_ENDPOINT
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
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_USER,
        expansions: Optional[List[str]] = DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]] = DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]] = DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    ):
        """
            expansions: ['pinned_tweet']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_USER else MAX_RESULTS_PER_PAGE_USER
        endpoint = USERS_LOOKUP_FOLLOWING_ENDPOINT
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
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        place_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: Optional[bool] = False,
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
        max_results = max_results if 5 <= max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_LIKED_TWEETS_ENDPOINT
        query = {'max_results': [str(max_results)]}
        tweets_lookup = TweetLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            user_fields=user_fields,
            place_fields=place_fields            
        )
        return tweets_lookup
    
    @GET(pagination=True)
    def get_users_that_liked_tweet(
        self,
        tweet_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        save: Optional[bool] = False,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_THAT_LIKED_TWEET_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<tweet_id>', tweet_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
        )
        return users_lookup

    @GET(pagination=True)
    def get_users_that_follow_list(
        self,
        list_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        save: Optional[bool] = False,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_THAT_FOLLOW_LIST_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<list_id>', list_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            user_fields=user_fields,
        )
        return users_lookup

    @GET(pagination=True)
    def get_list_members(
        self,
        list_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        save: Optional[bool] = False,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_LIST_MEMBERS_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<list_id>', list_id),
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
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        query: Optional[Dict[str, str]] = {}, 
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        place_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
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
        max_results = max_results if 5 <= max_results <= MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_MENTIONS_BY_ID_ENDPOINT
        query['max_results'] = [str(max_results)]
        tweets_lookup = TweetLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            user_fields=user_fields,
            place_fields=place_fields            
        )
        return tweets_lookup

    @GET
    def get_user_timelines_reverse_chronological(
        self,
        user_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        query: Dict[str, Any] = {},
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        place_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
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
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_TIMELINES_REVERSE_CHRONOLOGICAL_BY_ID_ENDPOINT
        query['max_results'] = [str(max_results)]
        tweets_lookup = TweetLookup(
            endpoint=endpoint.replace('<id>', user_id),
            query=query,
            expansions=expansions,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            user_fields=user_fields,
            place_fields=place_fields            
        )
        return tweets_lookup

    @GET
    def get_me(
        self,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: Optional[bool] = True,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        endpoint = USERS_LOOKUP_ME_ENDPOINT
        users_lookup = UsersLookup(
            endpoint=endpoint,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup

    @GET(pagination=True)    
    def get_blocked_users(
        self,
        user_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_USER,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: Optional[bool] = True,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_USER else MAX_RESULTS_PER_PAGE_USER
        endpoint = USERS_LOOKUP_BLOCKED_ENDPOINT
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
    def get_users_muted(
        self,
        user_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: Optional[bool] = True,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_MUTED_ENDPOINT
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
    def get_users_that_retweeted(
        self,
        tweet_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        save: Optional[bool] = True,
    ):
        """
            expansions: ['pinned_tweet_id']
        """
        max_results = max_results if max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_BY_RETWEET_ENDPOINT
        query = {'max_results': [str(max_results)]}
        users_lookup = UsersLookup(
            endpoint=endpoint.replace('<id>', tweet_id),
            query=query,
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields
        )
        return users_lookup
    
    @GET
    def get_tweets(
        self,
        tweet_ids: list,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: Optional[bool] = True,
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
        endpoint = TWEETS_LOOKUP_BY_USERS_ENDPOINT
        query = {'ids': tweet_ids}
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
    def get_user_bookmarked_tweets(
        self,
        user_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: Optional[bool] = True,
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
        max_results = max_results if 5 <= max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = USERS_LOOKUP_BOOKMARKS_ENDPOINT
        query = {'max_results': [str(max_results)]}
        tweet_lookup = TweetLookup(
            endpoint=endpoint.replace('<id>', user_id),
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
    def get_tweet(
        self,
        tweet_id: str,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: Optional[bool] = True,
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
        endpoint = TWEETS_LOOKUP_BY_ID_ENDPOINT
        tweet_lookup = TweetLookup(
            endpoint=endpoint.replace('<id>', tweet_id),
            expansions=expansions,
            user_fields=user_fields,
            tweet_fields=tweet_fields,
            media_fields=media_fields,
            poll_fields=poll_fields,
            place_fields=place_fields
        )
        return tweet_lookup

    @GET(pagination=True)
    def get_tweet_quotes(
        self,
        tweet_id: str,
        max_results: Optional[int] = MAX_RESULTS_PER_PAGE_DEFAULT,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
        save: Optional[bool] = True,
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
        max_results = max_results if 5 <= max_results < MAX_RESULTS_PER_PAGE_DEFAULT else MAX_RESULTS_PER_PAGE_DEFAULT
        endpoint = TWEETS_LOOKUP_TWEETS_QUOTES_ENDPOINT
        query = {'max_results': [str(max_results)]}
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

    @GET(pagination=True, app_only_auth=True)
    def tweet_recent_search(
        self,
        max_results: Optional[int] = 500,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        since_id: Optional[str] = None,
        until_id: Optional[str] = None,
        sort_order: Optional[str] = 'recency',
        qquery: Optional[str] = None,
        expansions: Optional[List[str]]= DEFAULT_USERS_LOOKUP_EXPANSION,
        user_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_USER_FIELDS,
        tweet_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        media_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        poll_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        place_fields: Optional[List[str]]= DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
    ):

        """
        :param start_time: Oldest UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param end_time: Newest UTC timestamp for tweets, format YYYY-MM-DDTHH:mm:ssZ.
        :param since_id: Greater than tweet id for response. Exclude this since_id.
        :param until_id: Less than tweet id for response. Exclude this until_id.
        :param sort_order: Sort by 'recency' or 'relevancy'
        :param qquery: build query with https://developer.twitter.com/apitools/api?endpoint=%2F2%2Ftweets%2Fsearch%2Fall&method=get"
        """
        max_results = 100 if max_results > 100 or max_results < 10 else max_results   
        query = dict()
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
            query['sort_order'] = [sort_order]
        query['max_results'] = [str(max_results)]
        
        tweet_lookup = TweetLookup(
            endpoint=TWEETS_LOOKUP_RECENT_SEARCH_ENDPOINT,
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
        count_fields = DEFAULT_TWEETS_LOOKUP_COUNT,
    ):

        endpoint = TWEETS_LOOKUP_RECENT_COUNT_ENDPOINT if recent else TWEETS_LOOKUP_ALL_COUNT_ENDPOINT
        query = {'max_results': [MAX_RESULTS_PER_PAGE_DEFAULT]}
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

    @POST
    def post_tweet(
        self,
        text: str,
        in_reply_to_tweet: Optional[str] = None,
    ):  
        endpoint = POST_TWEET_ENDPOINT
        payload = {'text': text}
        if in_reply_to_tweet:
            payload['reply'] = {
                'in_reply_to_tweet_id': in_reply_to_tweet
                }
        
        return endpoint, payload


