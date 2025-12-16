"""
Result Aggregator

Normalizes and aggregates data from different social media platforms.
"""

from typing import List, Dict, Any
from datetime import datetime
import logging
import hashlib

logger = logging.getLogger(__name__)


def normalize_schema(raw_data: List[Dict[str, Any]], source: str) -> List[Dict[str, Any]]:
    """
    Convert platform-specific data to unified schema.
    
    Args:
        raw_data: Raw data from scraper
        source: Platform name (TikTok, Instagram, etc.)
        
    Returns:
        List of normalized posts
    """
    normalized = []
    
    for item in raw_data:
        try:
            if source == "TikTok":
                post = normalize_tiktok(item)
            elif source == "Instagram":
                post = normalize_instagram(item)
            elif source == "Facebook":
                post = normalize_facebook(item)
            elif source == "Twitter":
                post = normalize_twitter(item)
            elif source == "RSS":
                post = normalize_rss(item)
            else:
                logger.warning(f"Unknown source: {source}")
                continue
            
            if post:
                normalized.append(post)
                
        except Exception as e:
            logger.error(f"Error normalizing {source} post: {e}")
            continue
    
    logger.info(f"Normalized {len(normalized)} posts from {source}")
    return normalized


def normalize_tiktok(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize TikTok data."""
    author_meta = item.get("authorMeta", {})
    
    return {
        "id": item.get("id", ""),
        "platform": "TikTok",
        "url": item.get("webVideoUrl", ""),
        "text": item.get("text", ""),
        "author": author_meta.get("name", "Unknown"),
        "author_followers": author_meta.get("fans", 0),
        "likes": item.get("diggCount", 0),
        "shares": item.get("shareCount", 0),
        "comments": item.get("commentCount", 0),
        "views": item.get("playCount", 0),
        "timestamp": item.get("createTime", datetime.now().isoformat()),
        "hashtags": item.get("hashtags", []),
        "thumbnail_url": item.get("covers", {}).get("default", "")
    }


def normalize_instagram(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Instagram data."""
    return {
        "id": item.get("id", ""),
        "platform": "Instagram",
        "url": item.get("url", ""),
        "text": item.get("caption", ""),
        "author": item.get("ownerUsername", "Unknown"),
        "author_followers": 0,  # Not always available
        "likes": item.get("likesCount", 0),
        "shares": 0,  # Instagram doesn't expose share count
        "comments": item.get("commentsCount", 0),
        "views": item.get("videoViewCount", 0),
        "timestamp": item.get("timestamp", datetime.now().isoformat()),
        "hashtags": item.get("hashtags", []),
        "thumbnail_url": item.get("displayUrl", "")
    }


def normalize_facebook(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Facebook data."""
    return {
        "id": item.get("postId", ""),
        "platform": "Facebook",
        "url": item.get("url", ""),
        "text": item.get("text", ""),
        "author": "Unknown",  # Often not available in public scraping
        "author_followers": 0,
        "likes": item.get("likes", 0),
        "shares": item.get("shares", 0),
        "comments": item.get("comments", 0),
        "views": 0,
        "timestamp": item.get("time", datetime.now().isoformat()),
        "hashtags": [],
        "thumbnail_url": ""
    }


def normalize_twitter(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Twitter data."""
    author = item.get("author", {})
    
    return {
        "id": item.get("id", ""),
        "platform": "Twitter",
        "url": item.get("tweetUrl", item.get("url", "")),  # tweet-scraper uses 'tweetUrl'
        "text": item.get("text", ""),
        "author": author.get("userName", "Unknown") if isinstance(author, dict) else "Unknown",
        "author_followers": author.get("followers", 0) if isinstance(author, dict) else 0,
        "likes": item.get("likeCount", 0),
        "shares": item.get("retweetCount", 0),
        "comments": item.get("replyCount", 0),
        "views": 0,
        "timestamp": item.get("createdAt", datetime.now().isoformat()),
        "hashtags": item.get("hashtags", []),
        "thumbnail_url": ""
    }


def normalize_rss(item: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize RSS feed data."""
    return {
        "id": hashlib.md5(item.get("link", "").encode()).hexdigest(),
        "platform": "RSS",
        "url": item.get("link", ""),
        "text": item.get("description", ""),
        "author": item.get("author", "Unknown"),
        "author_followers": 0,
        "likes": 0,
        "shares": 0,
        "comments": 0,
        "views": 0,
        "timestamp": item.get("pubDate", datetime.now().isoformat()),
        "hashtags": [],
        "thumbnail_url": ""
    }


def deduplicate_results(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate posts based on URL or content similarity.
    
    Args:
        posts: List of normalized posts
        
    Returns:
        Deduplicated list
    """
    seen_urls = set()
    unique_posts = []
    
    for post in posts:
        url = post.get("url", "")
        
        # Skip if URL already seen
        if url and url in seen_urls:
            continue
        
        seen_urls.add(url)
        unique_posts.append(post)
    
    logger.info(f"Deduplication: {len(posts)} -> {len(unique_posts)} posts")
    return unique_posts


def rank_by_score(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Sort posts by virality score (descending).
    
    Args:
        posts: List of scored posts
        
    Returns:
        Sorted list
    """
    sorted_posts = sorted(
        posts,
        key=lambda x: x.get("virality_score", 0),
        reverse=True
    )
    
    logger.info(f"Ranked {len(sorted_posts)} posts by score")
    return sorted_posts


def get_top_n(posts: List[Dict[str, Any]], n: int = 20) -> List[Dict[str, Any]]:
    """
    Get top N posts by score.
    
    Args:
        posts: List of scored and ranked posts
        n: Number of top posts to return
        
    Returns:
        Top N posts
    """
    top_posts = posts[:n]
    logger.info(f"Selected top {len(top_posts)} posts")
    return top_posts
