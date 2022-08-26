from __future__ import annotations 

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

from dataclass_wizard import JSONWizard

@dataclass
class UserEntitiesUrlObj:
    start: Optional[int] = field(default=None, repr=True)
    end: Optional[int] = field(default=None, repr=True)
    url: Optional[str] = field(default=None)
    expanded_url: Optional[str] = field(default=None, repr=True)
    display_url: Optional[str] = field(default=None, repr=True)


@dataclass
class UserEntitiesUrl:
    urls: Optional[List[UserEntitiesUrlObj]] = field(default=None)


@dataclass
class UserEntitiesTag:
    start: Optional[int] = field(default=None, repr=True)
    end: Optional[int] = field(default=None, repr=True)
    tag: Optional[str] = field(default=None, repr=True)



@dataclass
class UserEntitiesDescription:
    urls: Optional[List[UserEntitiesUrlObj]] = field(default=None, repr=True)
    hashtags: Optional[List[UserEntitiesTag]] = field(default=None, repr=True)
    mentions: Optional[List[UserEntitiesTag]] = field(default=None, repr=True)
    cashtags: Optional[List[UserEntitiesTag]] = field(default=None, repr=True)


@dataclass
class UserEntities:
    url: Optional[UserEntitiesUrl] = field(default=None)
    description: Optional[UserEntitiesDescription] = field(default=None, repr=True)


@dataclass
class UserPublicMetrics:
    followers_count: Optional[int] = field(default=None, repr=True)
    following_count: Optional[int] = field(default=None, repr=True)
    tweet_count: Optional[int] = field(default=None, repr=True)
    listed_count: Optional[int] = field(default=None, repr=True)
     

@dataclass
class UserWithheld:
    scope: Optional[str] = field(default=None)
    country_codes: Optional[List[str]] = field(default=None, repr=True)


@dataclass
class User(JSONWizard):
    id: Optional[str] = field(default=None, repr=True)
    name: Optional[str] = field(default=None, repr=True)
    username : Optional[str] = field(default=None, repr=True)
    created_at: Optional[str] = field(default=None, repr=True)
    description: Optional[str] = field(default=None, repr=True)
    entities: Optional[UserEntities] = field(default=None, repr=True)
    location: Optional[str] = field(default=None, repr=True)
    pinned_tweet_id: Optional[str] = field(default=None, repr=True)
    profile_image_url: Optional[str] = field(default=None, repr=True)
    protected: Optional[bool] = field(default=None, repr=True)
    public_metrics: Optional[UserPublicMetrics] = field(default=None, repr=True)
    url: Optional[str] = field(default=None, repr=True)
    verified: Optional[bool] = field(default=None, repr=True)
    withheld: Optional[UserWithheld] = field(default=None, repr=True, compare=False)
