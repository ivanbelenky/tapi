from dataclasses import dataclass
from typing import Any, Dict

import constants


@dataclass
class Lookup:
    endpoint: str
    user_fields: list = None,
    query: Dict[str, Any] = None
    expansions: list = None
    tweet_fields: list = None
    list_fields: list = None
    media_fields: list = None
    poll_fields: list = None
    place_fields: list = None
    count_fields: list = None
    
    def create_url(self):
        url = self.endpoint
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
        url += '' if not self.count_fields else f"&place.fields={','.join(self.count_fields)}"

        if len(url) > constants.MAX_URL_LENGTH:
            raise ValueError(f"User Lookup has too many fields too long: {url}")

        return url
    
    @staticmethod
    def next_page(url, response):
        token = response.json()['meta'].get('next_token')
        if token:
            next_page_url = url.replace("max_results", f"pagination_token={token}&max_results")
            return next_page_url
        return None

    @classmethod
    def paginate_responses(cls, responses):
        if responses and responses[0].get('data',False):
            data = responses[0]
            data_data = data['data']
            data_includes = data.get('includes')
            for res in responses[1:]:
                data_data.append(res['data'])
                if data_includes:
                    for field in constants.IMPLEMENTED_MODELS:
                        if data_includes.get(field, False):
                            data_includes[field].extend(res['includes'][field])
            return data
        return {}

    @classmethod
    def save_response(response):
        raise NotImplementedError


@dataclass
class UsersLookup(Lookup):
    def save_response(response):
        pass
    
@dataclass
class TweetLookup(Lookup):
    def save_response(response):
        pass

