from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

@dataclass
class UserEntitiesUrlObj:
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    url: Optional[str] = field(default=None)
    expanded_url: Optional[str] = field(default=None, repr=False)
    display_url: Optional[str] = field(default=None, repr=False)


@dataclass
class UserEntitiesUrl:
    urls: Optional[List[UserEntitiesUrlObj]] = field(default=None)


@dataclass
class UserEntitiesTag:
    start: Optional[int] = field(default=None, repr=False)
    end: Optional[int] = field(default=None, repr=False)
    tag: Optional[str] = field(default=None, repr=False)



@dataclass
class UserEntitiesDescription:
    urls: Optional[List[UserEntitiesUrlObj]] = field(default=None, repr=False)
    hashtags: Optional[List[UserEntitiesTag]] = field(default=None, repr=False)
    mentions: Optional[List[UserEntitiesTag]] = field(default=None, repr=False)
    cashtags: Optional[List[UserEntitiesTag]] = field(default=None, repr=False)


@dataclass
class UserEntities:
    url: Optional[UserEntitiesUrl] = field(default=None)
    description: Optional[UserEntitiesDescription] = field(default=None, repr=False)


@dataclass
class UserPublicMetrics:
    followers_count: Optional[str] = field(default=None, repr=False)
    following_count: Optional[str] = field(default=None, repr=False)
    tweet_count: Optional[str] = field(default=None, repr=False)
    listed_count: Optional[str] = field(default=None, repr=False)
     

@dataclass
class UserWithheld:
    scope: Optional[str] = field(default=None)
    country_codes: Optional[List[str]] = field(default=None, repr=False)


@dataclass
class User:
    id: Optional[str] = field(default=None, repr=False)
    name: Optional[str] = field(default=None, repr=False)
    username : Optional[str] = field(default=None, repr=False)
    created_at: Optional[datetime] = field(default=None, repr=False)
    description: Optional[str] = field(default=None, repr=False)
    entities: Optional[UserEntities] = field(default=None, repr=False)
    location: Optional[str] = field(default=None, repr=False)
    pinned_tweet_id: Optional[str] = field(default=None, repr=False)
    profile_image_url: Optional[str] = field(default=None, repr=False)
    protected: Optional[bool] = field(default=None, repr=False)
    public_metrics: Optional[UserPublicMetrics] = field(default=None, repr=False)
    url: Optional[str] = field(default=None, repr=False)
    verified: Optional[bool] = field(default=None, repr=False)
    withheld: Optional[UserWithheld] = field(default=None, repr=False, compare=False)
