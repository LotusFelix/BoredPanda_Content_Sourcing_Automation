"""
Category to Platform Hashtag Mapping

Maps BoredPanda content categories to platform-specific hashtags and keywords.
Research-backed mappings based on actual BoredPanda content analysis.
"""

from typing import List, Dict

# Category to platform-specific hashtags mapping
CATEGORY_HASHTAGS: Dict[str, Dict[str, List[str]]] = {
    "Funny": {
        "TikTok": ["fyp", "funny", "comedy", "memes", "foryou"],
        "Instagram": ["funny", "memes", "comedy", "lol", "funnyvideos"],
        "Twitter": ["funny", "memes", "comedy", "viral", "lol"],
        "Facebook": ["funny", "comedy", "memes"],
        "RSS": ["humor", "comedy", "funny news"]
    },
    "Animals": {
        "TikTok": ["animals", "cute", "pets", "dogs", "cats"],
        "Instagram": ["animals", "cute", "petsofinstagram", "dogsofinstagram", "catsofinstagram"],
        "Twitter": ["animals", "pets", "cute animals", "wildlife"],
        "Facebook": ["animals", "pets", "wildlife"],
        "RSS": ["animals", "pets", "wildlife news"]
    },
    "Relationships": {
        "TikTok": ["relationships", "dating", "marriage", "storytime"],
        "Instagram": ["relationships", "relationshipgoals", "dating", "marriage"],
        "Twitter": ["relationships", "dating", "AITA", "relationship advice"],
        "Facebook": ["relationships", "family", "marriage"],
        "RSS": ["relationships", "family news", "advice"]
    },
    "Art & Design": {
        "TikTok": ["art", "design", "creative", "artist"],
        "Instagram": ["art", "design", "artwork", "creativity", "artistsoninstagram"],
        "Twitter": ["art", "design", "creative", "artist"],
        "Facebook": ["art", "design", "creative"],
        "RSS": ["art", "design", "creativity"]
    },
    "Entertainment": {
        "TikTok": ["entertainment", "celebrity", "movies", "tv"],
        "Instagram": ["entertainment", "celebrity", "movies", "tvshows"],
        "Twitter": ["entertainment", "celebrity news", "movies", "TV"],
        "Facebook": ["entertainment", "celebrity", "movies"],
        "RSS": ["entertainment", "celebrity news", "Hollywood"]
    },
    "Curiosities": {
        "TikTok": ["interesting", "didyouknow", "facts", "todayilearned"],
        "Instagram": ["interesting", "facts", "knowledge", "didyouknow"],
        "Twitter": ["interesting", "TIL", "facts", "mind blown"],
        "Facebook": ["interesting", "facts", "curiosities"],
        "RSS": ["interesting news", "unusual", "facts"]
    },
    "Lifestyle": {
        "TikTok": ["lifestyle", "lifehacks", "wellness", "selfcare"],
        "Instagram": ["lifestyle", "wellness", "selfcare", "lifestyleblogger"],
        "Twitter": ["lifestyle", "wellness", "life tips"],
        "Facebook": ["lifestyle", "wellness", "life tips"],
        "RSS": ["lifestyle", "wellness", "life advice"]
    },
    "Society": {
        "TikTok": ["society", "social", "community", "awareness"],
        "Instagram": ["society", "social", "community", "socialissues"],
        "Twitter": ["society", "social issues", "community"],
        "Facebook": ["society", "social issues", "community"],
        "RSS": ["society", "social issues", "community news"]
    },
    "Entertainment News": {
        "TikTok": ["celebritynews", "gossip", "hollywood"],
        "Instagram": ["celebritynews", "gossip", "enews"],
        "Twitter": ["celebrity news", "Hollywood gossip", "entertainment news"],
        "Facebook": ["celebrity news", "entertainment news"],
        "RSS": ["celebrity news", "entertainment news", "Hollywood news"]
    },
    "Politics": {
        "TikTok": ["politics", "news", "political"],
        "Instagram": ["politics", "political", "news"],
        "Twitter": ["politics", "political news", "breaking news"],
        "Facebook": ["politics", "political news"],
        "RSS": ["politics", "political news", "government"]
    }
}

# RSS feed URLs by category
RSS_FEEDS: Dict[str, List[str]] = {
    "Funny": ["https://www.reddit.com/r/funny/.rss"],
    "Animals": ["https://www.reddit.com/r/aww/.rss"],
    "Relationships": ["https://www.reddit.com/r/relationships/.rss"],
    "Art & Design": ["https://www.reddit.com/r/Art/.rss"],
    "Entertainment": [
        "https://rss.nytimes.com/services/xml/rss/nyt/Movies.xml"
    ],
    "Curiosities": ["https://www.reddit.com/r/todayilearned/.rss"],
    "Lifestyle": ["https://www.reddit.com/r/LifeProTips/.rss"],
    "Society": ["https://www.reddit.com/r/news/.rss"],
    "Entertainment News": [
        "https://rss.nytimes.com/services/xml/rss/nyt/Movies.xml"
    ],
    "Politics": ["https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml"]
}


def get_hashtags(category: str, platform: str) -> List[str]:
    """
    Get platform-specific hashtags for a given category.
    
    Args:
        category: BoredPanda category (e.g., "Funny", "Animals")
        platform: Social platform (e.g., "TikTok", "Instagram")
        
    Returns:
        List of hashtags/keywords for the platform
        
    Raises:
        ValueError: If category or platform is invalid
    """
    if category not in CATEGORY_HASHTAGS:
        # Fallback to generic viral hashtags
        return ["viral", "trending", "fyp"]
    
    if platform not in CATEGORY_HASHTAGS[category]:
        return []
    
    return CATEGORY_HASHTAGS[category][platform]


def get_rss_feeds(category: str) -> List[str]:
    """
    Get RSS feed URLs for a given category.
    
    Args:
        category: BoredPanda category
        
    Returns:
        List of RSS feed URLs
    """
    return RSS_FEEDS.get(category, [])


def get_all_categories() -> List[str]:
    """Get list of all supported categories."""
    return list(CATEGORY_HASHTAGS.keys())


def get_all_platforms() -> List[str]:
    """Get list of all supported platforms."""
    return ["TikTok", "Instagram", "Facebook", "Twitter", "RSS"]
