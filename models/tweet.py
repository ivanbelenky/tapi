from __future__ import annotations 

from dataclasses import dataclass, field
from multiprocessing import context
from typing import Optional, List

from dataclass_wizard import JSONWizard

@dataclass
class TweetAttachments:
    poll_ids: Optional[List[str]] = field(default=None, repr=True, compare=False)
    media_keys: Optional[List[str]] = field(default=None, repr=True, compare=False)


@dataclass
class TweetContextAnnotationsDomain:
    id: Optional[str] = field(default=None, repr=True)
    name: Optional[str] = field(default=None, repr=True)
    description: Optional[str] = field(default=None, repr=True)


@dataclass
class TweetContextAnnotationsEntity:
    id: Optional[str] = field(default=None, repr=True)
    name: Optional[str] = field(default=None, repr=True)
    description: Optional[str] = field(default=None, repr=True)


@dataclass
class TweetContextAnnotations:
    domain: Optional[TweetContextAnnotationsDomain] = field(default=None, repr=True)
    entity: Optional[TweetContextAnnotationsEntity] = field(default=None, repr=True)


@dataclass
class TweetEntitiesAnnotations:
    start: Optional[int] = field(default=None, repr=True)
    end: Optional[int] = field(default=None, repr=True)
    probability: Optional[float] = field(default=None, repr=True)
    type: Optional[str] = field(default=None, repr=True)
    normalized_text: Optional[str] = field(default=None, repr=True)


@dataclass
class TweetEntitiesTag:
    start: Optional[int] = field(default=None, repr=True)
    end: Optional[int] = field(default=None, repr=True)
    tag: Optional[str] = field(default=None, repr=True)
    

@dataclass
class TweetEntitiesUrl:
    start: Optional[int] = field(default=None, repr=True)
    end: Optional[int] = field(default=None, repr=True)
    url: Optional[str] = field(default=None, repr=True)
    expanded_url: Optional[str] = field(default=None, repr=True)
    display_url: Optional[str] = field(default=None, repr=True)
    status: Optional[str] = field(default=None, repr=True)
    title: Optional[str] = field(default=None, repr=True)
    description: Optional[str] = field(default=None, repr=True)
    unknown_url: Optional[str] = field(default=None, repr=True)

    
@dataclass
class TweetEntities:
    annotations: Optional[List[TweetEntitiesAnnotations]]
    cashtags: Optional[List[TweetEntitiesTag]]
    hashtags: Optional[List[TweetEntitiesTag]]
    mentions: Optional[List[TweetEntitiesTag]]
    urls: Optional[List[TweetEntitiesUrl]]


@dataclass
class Coordinates:
    type: Optional[str] = field(default=None, repr=True)
    coordinates: Optional[List[float]] = field(default=None, repr=True)


@dataclass
class TweetGeo:
    coordinates: Optional[Coordinates] = field(default=None, repr=True)
    place_id: Optional[str] = field(default=None, repr=True)


@dataclass
class TweetNonPublicMetrics:
    impression_count: Optional[int] = field(default=None, repr=True)
    url_link_clicks: Optional[int] = field(default=None, repr=True)
    user_profile_clicks: Optional[int] = field(default=None, repr=True)


@dataclass
class TweetMainMetrics:
    impression_count: Optional[int] = field(default=None, repr=True)
    like_count: Optional[int] = field(default=None, repr=True)
    reply_count: Optional[int] = field(default=None, repr=True)
    retweet_count: Optional[int] = field(default=None, repr=True)
    url_link_clicks: Optional[int] = field(default=None, repr=True)
    user_profile_clicks: Optional[int] = field(default=None, repr=True)


@dataclass
class TweetPublicMetrics:
    retweet_count: Optional[int] = field(default=None, repr=True)
    reply_count: Optional[int] = field(default=None, repr=True)
    like_count: Optional[int] = field(default=None, repr=True)
    quote_count: Optional[int] = field(default=None, repr=True)
    

@dataclass
class TweetReferencedTweets:
    type: Optional[str] = field(default=None, repr=True)
    id: Optional[str] = field(default=None, repr=True)


@dataclass
class TweetWithheld:
    copyright: Optional[str] = field(default=None, repr=True)
    country_codes: Optional[List[str]] = field(default=None, repr=True)


@dataclass 
class Tweet(JSONWizard):
    id: Optional[str] = field(default=None, repr=True)
    text: Optional[str] = field(default=None, repr=True)
    attachments: Optional[TweetAttachments] = field(default=None, repr=True)
    author_id: Optional[str] = field(default=None, repr=True)
    context_annotations: Optional[List[TweetContextAnnotations]] = field(default=None, repr=True)
    conversation_id: Optional[str] = field(default='', repr=True)
    created_at: Optional[str] = field(default=None, repr=True)
    entities: Optional[TweetEntities] = field(default=None, repr=True)
    geo: Optional[TweetGeo] = field(default=None, repr=True)
    in_reply_to_user_id: Optional[str] = field(default=None, repr=True) 
    lang: Optional[str] = field(default=None, repr=True)
    non_public_metrics: Optional[TweetNonPublicMetrics] = field(default=None, repr=True)
    organic_metrics: Optional[TweetMainMetrics] = field(default=None, repr=True)
    possibly_sensitive: Optional[bool] = field(default=None, repr=True)
    promoted_metrics: Optional[TweetMainMetrics] = field(default=None, repr=True)
    public_metrics: Optional[TweetPublicMetrics] = field(default=None, repr=True)
    referenced_tweets: Optional[List[TweetReferencedTweets]] = field(default=None, repr=True)
    reply_settings: Optional[str] = field(default=None, repr=True)
    source: Optional[str] = field(default=None, repr=True)
    withheld: Optional[TweetWithheld] = field(default=None, repr=True)

