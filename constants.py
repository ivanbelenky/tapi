MAX_URL_LENGTH = 500
MAX_RESULTS_PER_PAGE = '100'
MAX_PAGES = 10

ALL_USER_FIELDS = [
    'id',
    'username',
    'name',
    'description',
    'url',
    'profile_image_url',
    'verified',
    'created_at',
    'entities',
    'location',
    'pinned_tweet_id',
    'protected',
    'public_metrics',
    'withheld'
]

ALL_TWEET_FIELDS = [
    'id',
    'author_id',
    'text',
    'created_at',
    'in_reply_to_user_id',
    'referenced_tweets',
    'conversation_id',
    'attachments',
    'context_annotations',
    'entities',
    'geo',
    'lang',
    'non_public_metrics',
    'organic_metrics',
    'possibly_sensitive',
    'promoted_metrics',
    'public_metrics',
    'reply_settings',
    'source',
    'withheld'
]

ALL_LIST_FIELDS = [
    'id',
    'name',
    'description',
    'follower_count',
    'owner_id',    
    'created_at',
    'member_count',
    'private'
]

ALL_MEDIA_FIELDS = [
    'alt_text',
    'duration_ms',
    'height',
    'media_key',
    'non_public_metrics',
    'organic_metrics',
    'preview_image_url',
    'promoted_metrics',
    'public_metrics',
    'type',
    'url',
    'variants',
    'width'
]

ALL_POLL_FIELDS = [
    'duration_minutes',
    'end_datetime',
    'id',
    'options',
    'voting_status'
]

ALL_PLACE_FIELDS = [
    'id',
    'country',
    'name',
    'full_name',
    'geo',
    'contained_within',
    'country_code',
    'place_type'
]

USERS_LOOKUP_BY_ID_ENDPOINT = "https://api.twitter.com/2/users"
USERS_LOOKUP_BY_USERNAME_ENDPOINT = "https://api.twitter.com/2/users/by"
USERS_LOOKUP_BY_USERNAME_REGEX_ENDPOINT = "https://api.twitter.com/2/users/by/username/<username>"
USERS_LOOKUP_BY_USERNAME_ID_ENDPOINT = "https://api.twitter.com/2/users/<id>"
USERS_LOOKUP_FOLLOWED_LISTS_BY_ID_ENDPOINT = "https://api.twitter.com/2/users/<id>/followed_lists"
USERS_LOOKUP_OWNED_LISTS_BY_ID_ENDPOINT = "https://api.twitter.com/2/users/<id>/owned_lists"
USERS_LOOKUP_LIST_MEMBERSHIPS_BY_ID_ENDPOINT = "https://api.twitter.com/2/users/<id>/list_memberships"
USERS_LOOKUP_PINNED_LISTS_BY_ID_ENDPOINT = "https://api.twitter.com/2/users/<id>/list_memberships"
USERS_LOOKUP_FOLLOWERS_ENDPOINT = "https://api.twitter.com/2/users/<id>/followers"
USERS_LOOKUP_FOLLOWING_ENDPOINT = "https://api.twitter.com/2/users/<id>/following"
USERS_LOOKUP_LIKED_TWEETS_ENDPOINT = "https://api.twitter.com/2/users/<id>/liked_tweets"
USERS_LOOKUP_MENTIONS_BY_ID_ENDPOINT = "https://api.twitter.com/2/users/<id>/mentions"
USERS_LOOKUP_TIMELINES_REVERSE_CHRONOLOGICAL_BY_ID_ENDPOINT = "https://api.twitter.com/2/users/<id>/timelines/reverse_chronological"
USERS_LOOKUP_ME_ENDPOINT = "https://api.twitter.com/2/users/me"

DEFAULT_USERS_LOOKUP_EXPANSION = []
DEFAULT_USERS_LOOKUP_USER_FIELDS = ALL_USER_FIELDS[:6]
DEFAULT_USERS_LOOKUP_TWEET_FIELDS = ALL_TWEET_FIELDS[:7]
DEFAULT_USERS_LOOKUP_LIST_FIELDS = ALL_LIST_FIELDS[:5]
DEFAULT_USERS_LOOKUP_MEDIA_FIELDS = []
DEFAULT_USERS_LOOKUP_POLL_FIELDS = []
DEFAULT_USERS_LOOKUP_PLACE_FIELDS = ALL_PLACE_FIELDS[:3]