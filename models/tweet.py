from dataclasses import dataclass, field
from datetime import datetime
from html import entities
from typing import Optional, List


@dataclass
class TweetAttachments:
    poll_ids: Optional[List[str]] = field(default=None, repr=False, compare=False)
    media_keys: Optional[List[str]] = field(default=None, repr=False, compare=False)


@dataclass
class TweetContextAnnotationsDomain:
    id: Optional[str] = field(default=None, repr=False)
    name: Optional[str] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)


@dataclass
class TweetContextAnnotationsEntity:
    id: Optional[str] = field(default=None, repr=False)
    name: Optional[str] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)


@dataclass
class TweetContextAnnotations:
    domain: Optional[TweetContextAnnotationsDomain] = field(default=None, repr=False)
    entity: Optional[TweetContextAnnotationsEntity] = field(default=None, repr=False)


@dataclass
class TweetEntitiesAnnotations:
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    probability: Optional[float] = field(default=None, repr=False)
    type: Optional[str] = field(default=None, repr=False)
    normalized_text: Optional[str] = field(default=None, repr=False)


@dataclass
class TweetEntitiesTag:
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    tag: Optional[str] = field(default=None, repr=False)
    

@dataclass
class TweetEntitiesUrl:
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    url: Optional[str] = field(default=None, repr=False)
    expanded_url: Optional[str] = field(default=None, repr=False)
    display_url: Optional[str] = field(default=None, repr=False)
    status: Optional[str] = field(default=None, repr=False)
    title: Optional[str] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)
    unknown_url: Optional[str] = field(default=None, repr=False)

    
@dataclass
class TweetEntities:
    annotations: Optional[List[TweetEntitiesAnnotations]]
    cashtags: Optional[List[TweetEntitiesTag]]
    hashtags: Optional[List[TweetEntitiesTag]]
    mentions: Optional[List[TweetEntitiesTag]]
    urls: Optional[List[TweetEntitiesUrl]]


@dataclass
class Coordinates:
    type: Optional[str] = field(default=None, repr=False)
    coordinates: Optional[List[float]] = field(default=None, repr=False)


@dataclass
class TweetGeo:
    coordinates: Optional[Coordinates] = field(default=None, repr=False)
    place_id: Optional[str] = field(default=None, repr=False)


@dataclass
class TweetNonPublicMetrics:
    impression_count: Optional[int] = field(default=None, repr=False)
    url_link_clicks: Optional[int] = field(default=None, repr=False)
    user_profile_clicks: Optional[int] = field(default=None, repr=False)


@dataclass
class TweetMainMetrics:
    impression_count: Optional[int] = field(default=None, repr=False)
    like_count: Optional[int] = field(default=None, repr=False)
    reply_count: Optional[int] = field(default=None, repr=False)
    retweet_count: Optional[int] = field(default=None, repr=False)
    url_link_clicks: Optional[int] = field(default=None, repr=False)
    user_profile_clicks: Optional[int] = field(default=None, repr=False)


@dataclass
class TweetPublicMetrics:
    retweet_count: Optional[int] = field(default=None, repr=False)
    reply_count: Optional[int] = field(default=None, repr=False)
    like_count: Optional[int] = field(default=None, repr=False)
    quote_count: Optional[int] = field(default=None, repr=False)
    

@dataclass
class TweetReferencedTweets:
    type: Optional[str] = field(default=None, repr=False)
    id: Optional[str] = field(default=None, repr=False)


@dataclass
class TweetWithheld:
    copyright: Optional[str] = field(default=None, repr=False)
    country_codes: Optional[List[str]] = field(default=None, repr=False)


@dataclass 
class Tweet:
    id: Optional[str] = field(default=None, repr=False)
    text: Optional[str] = field(default=None, repr=False)
    attachments: Optional[TweetAttachments] = field(default=None, repr=False)
    author_id: Optional[str] = field(default=None, repr=False)
    context_annotations: Optional[List[TweetContextAnnotations]] = field(default=None, repr=False)
    conversation_id: Optional[str] = field(default='', repr=False)
    created_at: Optional[datetime] = field(default=None, repr=False)
    entities: Optional[TweetEntities] = field(default=None, repr=False)
    geo: Optional[TweetGeo] = field(default=None, repr=False)
    in_reply_to_user: Optional[str] = field(default=None, repr=False) 
    lang: Optional[str] = field(default=None, repr=False)
    non_public_metrics: Optional[TweetNonPublicMetrics] = field(default=None, repr=False)
    organic_metrics: Optional[TweetMainMetrics] = field(default=None, repr=False)
    possibly_sensitive: Optional[bool] = field(default=None, repr=False)
    promoted_metrics: Optional[TweetMainMetrics] = field(default=None, repr=False)
    public_metrics: Optional[TweetPublicMetrics] = field(default=None, repr=False)
    referenced_tweets: Optional[List[TweetReferencedTweets]] = field(default=None, repr=False)
    reply_settings: Optional[str] = field(default=None, repr=False)
    source: Optional[str] = field(default=None, repr=False)
    withheld: Optional[TweetWithheld] = field(default=None, repr=False)


