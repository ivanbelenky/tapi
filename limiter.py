LIMITER = {
    "get_users": { 
        'scopes' : ['tweet.read', 'user.read', 'offline.access'],
        'limit': 900,
        'auth': 'BEARER_TOKEN'
    },
    "get_users_by_usernames": { 
        'scopes' : ['tweet.read', 'user.read', 'offline.access'],
        'limit': 900,
        'auth': 'BEARER_TOKEN'
    },
    "get_users_by_username_regex": { 
        'scopes' : ['tweet.read', 'user.read', 'offline.access'],
        'limit': 900,
        'auth': 'BEARER_TOKEN'
    },
    "get_single_user": { 
        'scopes' : ['tweet.read', 'user.read', 'offline.access'],
        'limit': 900,
        'auth': 'BEARER_TOKEN'
    },
    "get_user_followed_lists": { 
        'scopes' : ['tweet.read', 'user.read', 'list.read' 'offline.access'],
        'limit': 15,
        'auth': 'BEARER_TOKEN'
    },
    "get_user_list_membership": { 
        'scopes' : ['tweet.read', 'user.read', 'list.read' 'offline.access'],
        'limit': 15,
        'auth': 'BEARER_TOKEN'
    },
    "get_users_owned_lists": { 
        'scopes' : ['tweet.read', 'user.read', 'list.read' 'offline.access'],
        'limit': 15,
        'auth': 'BEARER_TOKEN'
    },
    "get_users_pinned_lists": { 
        'scopes' : ['tweet.read', 'user.read', 'list.read' 'offline.access'],
        'limit': 15,
        'auth': 'BEARER_TOKEN'
    },
    "get_user_followers": { 
        'scopes' : ['tweet.read', 'user.read', 'follows.read', 'offline.access'],
        'limit': 15,
        'auth': 'BEARER_TOKEN'
    },
    "get_user_following": { 
        'scopes' : ['tweet.read', 'user.read', 'follows.read', 'offline.access'],
        'limit': 15,
        'auth': 'BEARER_TOKEN'
    },
    "get_user_liked_tweets": { 
        'scopes' : ['tweet.read', 'user.read', 'like.read', 'offline.access'],
        'limit': 75,
        'auth': 'BEARER_TOKEN'
    },
    "get_users_that_liked_tweet": { 
        'scopes' : ['tweet.read', 'user.read', 'like.read', 'offline.access'],
        'limit': 75,
        'auth': 'BEARER_TOKEN'
    },
    "get_users_that_follow_list": {
        'scopes': ['tweet.read', 'users.read', 'list.read', 'offline.access'],
        'limit': 180,
        'auth': 'BEARER_TOKEN'
    },
    "get_list_members": {
        'scopes': ['tweet.read', 'users.read', 'list.read', 'offline.access'],
        'limit': 900,
        'auth': 'BEARER_TOKEN'
    },
    "get_user_mentions": { 
        'scopes' : ['tweet.read', 'user.read', 'offline.access'],
        'limit': 180,
        'auth': 'BEARER_TOKEN'
    },
    "get_user_timelines_reverse_chronological": { 
        'scopes' : ['tweet.read', 'user.read', 'offline.access'],
        'limit': 180,
        'auth': 'OAUTH_SIGNATURE'
    },
    "get_me": { 
        'scopes' : ['tweet.read', 'user.read', 'offline.access'],
        'limit': 75,
        'auth': 'OAUTH_SIGNATURE'
    },
    "get_blocked_users": { 
        'scopes' : ['tweet.read', 'user.read', 'block.read', 'offline.access'],
        'limit': 15,
        'auth': 'OAUTH_SIGNATURE'
    },
    "get_users_muted": { 
        'scopes' : ['tweet.read', 'user.read', 'mute.read', 'offline.access'],
        'limit': 15,
        'auth': 'OAUTH_SIGNATURE'
    },
    "get_users_that_retweeted": { 
        'scopes' : ['tweet.read', 'user.read', 'offline.access'],
        'limit': 75,
        'auth': 'BEARER_TOKEN'
    },
    'post_tweet': {
        'scopes' : ['tweet.read', 'tweet.write', 'users.read', 'offline.access'],
        'limit': 200,
        'auth': 'OAUTH_SIGNATURE'
    },
    'tweet_recent_search': {
        'scopes': ['tweet.read', 'tweet.write', 'users.read', 'offline.access'],
        'limit': 900,
        'auth': 'BEARER_TOKEN'
    }
}