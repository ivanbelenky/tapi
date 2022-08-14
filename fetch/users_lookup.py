from dataclasses import dataclass
from typing import Any, Dict

from constants import (
    DEFAULT_USERS_LOOKUP_EXPANSION,
    DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    DEFAULT_USERS_LOOKUP_USER_FIELDS,
    DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
    DEFAULT_USERS_LOOKUP_POLL_FIELDS,
    DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
    USERS_LOOKUP_BY_ID_ENDPOINT,
    USERS_LOOKUP_BY_USERNAME_ENDPOINT,
    USERS_LOOKUP_BY_USERNAME_REGEX_ENDPOINT,
    USERS_LOOKUP_BY_USERNAME_ID_ENDPOINT,
    USERS_LOOKUP_FOLLOWED_LISTS_BY_ID_ENDPOINT,
    USERS_LOOKUP_LIST_MEMBERSHIPS_BY_ID_ENDPOINT,
    USERS_LOOKUP_OWNED_LISTS_BY_ID_ENDPOINT,
    USERS_LOOKUP_PINNED_LISTS_BY_ID_ENDPOINT,
    USERS_LOOKUP_FOLLOWERS_ENDPOINT,
    USERS_LOOKUP_FOLLOWING_ENDPOINT,
    USERS_LOOKUP_LIKED_TWEETS_ENDPOINT,
    USERS_LOOKUP_MENTIONS_BY_ID_ENDPOINT,
    USERS_LOOKUP_TIMELINES_REVERSE_CHRONOLOGICAL_BY_ID_ENDPOINT,
    USERS_LOOKUP_ME_ENDPOINT,
    MAX_URL_LENGTH,
    MAX_RESULTS_PER_PAGE,
)

@dataclass
class UsersLookup:
    endpoint: str
    user_fields: list
    query: Dict[str, Any] = None
    expansions: list = None
    tweet_fields: list = None
    list_fields: list = None
    media_fields: list = None
    poll_fields: list = None
    place_fields: list = None
    response: Dict[str, Any] = None
    
    def create_url(self):
        url = f"{self.endpoint}"
        url += '?' if self.list_fields or self.user_fields \
            or self.expansions or self.tweet_fields \
            or self.media_fields or self.poll_fields \
            or self.place_fields or self.query else ''
        if self.query:
            for q, values in self.query.items():
                url += f"{q}={','.join(values)}"
        url += '' if not self.user_fields else f"&user.fields={','.join(self.user_fields)}" 
        url += '' if not self.list_fields else f"&list.fields={','.join(self.list_fields)}"
        url += '' if not self.expansions else f"&expansions={','.join(self.expansions)}" 
        url += '' if not self.tweet_fields else f"&tweet.fields={','.join(self.tweet_fields)}"
        url += '' if not self.media_fields else f"&media.fields={','.join(self.media_fields)}"
        url += '' if not self.poll_fields else f"&poll.fields={','.join(self.poll_fields)}"
        url += '' if not self.place_fields else f"&place.fields={','.join(self.place_fields)}"

        if len(url) > MAX_URL_LENGTH:
            raise ValueError(f"User Lookup has too many fields too long: {url}")

        return url
    
    @staticmethod
    def next_page(url, response):
        token = response.json()['meta']['next_token']
        next_page_url = url.replace("max_results", f"pagination_token={token}&max_results")
        return next_page_url

def get_users_by_id_url(
    users_ids: list, 
    use_default: bool = True, 
    expansions: list = None, 
    user_fields: list = None, 
    tweet_fields: list = None
):
    ids = [str(int(usr_id)) for usr_id in users_ids]
    kwargs = {
        'endpoint': USERS_LOOKUP_BY_ID_ENDPOINT,
        'query': {'ids': ids},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_TWEET_FIELDS
    }
    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()
        
        
def get_users_by_usernames_url(
    usernames: list, 
    use_default: bool = True, 
    expansions: list = None, 
    user_fields: list = None, 
    tweet_fields: list = None
):
    kwargs = {
        'endpoint': USERS_LOOKUP_BY_USERNAME_ENDPOINT,
        'query': {'usernames': usernames},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_TWEET_FIELDS
    }
    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_users_by_username_regex_url(
    username: str, 
    use_default: bool = True, 
    expansions: list = None, 
    user_fields: list = None, 
    tweet_fields: list = None
):
    kwargs = {
        'endpoint': USERS_LOOKUP_BY_USERNAME_REGEX_ENDPOINT.replace('<username>', username),
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    }
    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_user_by_id_url(
    user_id: str, 
    use_default: bool = True, 
    expansions: list = None, 
    user_fields: list = None, 
    tweet_fields: list = None
):
    kwargs = {
        'endpoint': USERS_LOOKUP_BY_USERNAME_ID_ENDPOINT.replace('<id>', user_id),
        'query': {},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    }
    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_users_followed_lists_by_id_url(
    user_id: str, 
    use_default: bool = True, 
    expansions: list = None, 
    user_fields: list = None, 
    list_fields: list = None
):
    kwargs = {
        'endpoint': USERS_LOOKUP_FOLLOWED_LISTS_BY_ID_ENDPOINT.replace('<id>', user_id),
        'query': {'max_results': [MAX_RESULTS_PER_PAGE]},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'list_fields': list_fields if list_fields or not use_default else DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    }
    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_users_list_memberships_by_id_url(
    user_id: str, 
    use_default: bool = True, 
    expansions: list = None, 
    user_fields: list = None, 
    list_fields: list = None
):
    kwargs = {
        'endpoint': USERS_LOOKUP_LIST_MEMBERSHIPS_BY_ID_ENDPOINT.replace('<id>', user_id),
        'query': {'max_results': [MAX_RESULTS_PER_PAGE]},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'list_fields': list_fields if list_fields or not use_default else DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    }
    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_users_owned_lists_by_id_url(
    user_id: str, 
    use_default: bool = True, 
    expansions: list = None, 
    user_fields: list = None, 
    list_fields: list = None
):
    kwargs = {
        'endpoint': USERS_LOOKUP_OWNED_LISTS_BY_ID_ENDPOINT.replace('<id>', user_id),
        'query': {'max_results': [MAX_RESULTS_PER_PAGE]},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'list_fields': list_fields if list_fields or not use_default else DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    }
    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_users_pinned_lists_by_id_url(
    user_id: str, 
    use_default: bool = True, 
    expansions: list = None, 
    user_fields: list = None, 
    list_fields: list = None
):
    kwargs = {
        'endpoint': USERS_LOOKUP_PINNED_LISTS_BY_ID_ENDPOINT.replace('<id>', user_id),
        'query': {'max_results': [MAX_RESULTS_PER_PAGE]},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'list_fields': list_fields if list_fields or not use_default else DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    }
    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_user_followers_by_id_url(
    user_id: str,
    use_default: bool = True,
    expansions: list = None,
    user_fields: list = None,
    tweet_fields: list = None,
):
    id = str(int(user_id))
    kwargs = { 
        'endpoint': USERS_LOOKUP_FOLLOWERS_ENDPOINT.replace('<id>', id),
        'query': {'max_results': [MAX_RESULTS_PER_PAGE]},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
    }

    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_user_following_by_id_url(
    user_id: str,
    use_default: bool = True,
    expansions: list = None,
    user_fields: list = None,
    tweet_fields: list = None,
):
    id = str(int(user_id))
    kwargs = { 
        'endpoint': USERS_LOOKUP_FOLLOWING_ENDPOINT.replace('<id>', id),
        'query': {'max_results': [MAX_RESULTS_PER_PAGE]},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    }

    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_user_liked_tweets_by_id_url(
    user_id: str,
    use_default: bool = True,
    expansions: list = None,
    tweet_fields: list = None,
    media_fields: list = None,
    poll_fields: list = None,
    user_fields: list = None,
    place_fields: list = None,
):
    id = str(int(user_id))
    kwargs = { 
        'endpoint': USERS_LOOKUP_LIKED_TWEETS_ENDPOINT.replace('<id>', id),
        'query': {'max_results': [MAX_RESULTS_PER_PAGE]},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        'media_fields': media_fields if media_fields or not use_default else DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        'poll_fields': poll_fields if poll_fields or not use_default else DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,        
        'place_fields': place_fields if place_fields or not use_default else DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
    }

    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_user_mentions_by_id_url(
    user_id: str,
    query: dict,
    use_default: bool = True,
    expansions: list = None,
    tweet_fields: list = None,
    media_fields: list = None,
    poll_fields: list = None,
    user_fields: list = None,
    place_fields: list = None,
):

    id = str(int(user_id))
    query['max_results'] = [MAX_RESULTS_PER_PAGE]
    kwargs = { 
        'endpoint': USERS_LOOKUP_MENTIONS_BY_ID_ENDPOINT.replace('<id>', id),
        'query': query,
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        'media_fields': media_fields if media_fields or not use_default else DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        'poll_fields': poll_fields if poll_fields or not use_default else DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,        
        'place_fields': place_fields if place_fields or not use_default else DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
    }

    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_user_timelines_reverse_chronological_by_id_url(
    user_id: str,
    query: dict,
    use_default: bool = True,
    expansions: list = None,
    tweet_fields: list = None,
    media_fields: list = None,
    poll_fields: list = None,
    user_fields: list = None,
    place_fields: list = None,
):

    id = str(int(user_id))
    query['max_results'] = [MAX_RESULTS_PER_PAGE]
    kwargs = { 
        'endpoint': USERS_LOOKUP_TIMELINES_REVERSE_CHRONOLOGICAL_BY_ID_ENDPOINT.replace('<id>', id),
        'query': query,
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_TWEET_FIELDS,
        'media_fields': media_fields if media_fields or not use_default else DEFAULT_USERS_LOOKUP_MEDIA_FIELDS,
        'poll_fields': poll_fields if poll_fields or not use_default else DEFAULT_USERS_LOOKUP_POLL_FIELDS,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,        
        'place_fields': place_fields if place_fields or not use_default else DEFAULT_USERS_LOOKUP_PLACE_FIELDS,
    }

    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()




def get_me_url(
    use_default: bool = True,
    expansions: list = None,
    user_fields: list = None,
    tweet_fields: list = None,
):
    kwargs = { 
        'endpoint': USERS_LOOKUP_ME_ENDPOINT,
        'query': {'max_results': [MAX_RESULTS_PER_PAGE]},
        'expansions': expansions if expansions or not use_default else DEFAULT_USERS_LOOKUP_EXPANSION,
        'user_fields': user_fields if user_fields or not use_default else DEFAULT_USERS_LOOKUP_USER_FIELDS,
        'tweet_fields': tweet_fields if tweet_fields or not use_default else DEFAULT_USERS_LOOKUP_LIST_FIELDS,
    }

    user_lookup = UsersLookup(**kwargs)
    return user_lookup.create_url()


def get_blocked_users_by_id_url():
    #needs OAUTH_SIGNATURE
    pass


def get_users_bookmarks_by_id_url():
    #needs OAUTH_SIGNATURE
    pass


def get_muted_users_by_id_url():
    #needs OAUTH SIGNATURE
    pass