"""
Language Filter Utility

Detects and filters content based on language.
"""

import re
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


def is_likely_english(text: str) -> bool:
    """
    Heuristic check if text is likely English.
    
    Uses simple rules:
    - Checks for common English words
    - Checks character set (primarily Latin alphabet)
    - Filters out obvious non-English scripts
    
    Args:
        text: Text to check
        
    Returns:
        True if likely English, False otherwise
    """
    if not text or len(text.strip()) < 10:
        return True  # Too short to determine, allow it
    
    text_lower = text.lower()
    
    # Common English words (高频词)
    common_words = [
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it' 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what'
    ]
    
    # Count how many common English words appear
    word_count = 0
    for word in common_words:
        if f' {word} ' in f' {text_lower} ':
            word_count += 1
    
    # If at least 2 common words found, likely English
    if word_count >= 2:
        return True
    
    # Check for non-Latin scripts (CJK, Arabic, Cyrillic, etc.)
    non_latin_pattern = re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\u0400-\u04ff\u0600-\u06ff\u0750-\u077f]')
    non_latin_chars = len(non_latin_pattern.findall(text))
    
    # If more than 20% non-Latin characters, likely not English
    if len(text) > 0 and non_latin_chars / len(text) > 0.2:
        return False
    
    # Check for basic English sentence structure (spaces between words)
    words = text.split()
    if len(words) < 3:
        return True  # Too few words to determine
    
    # If we have reasonable word count and no non-Latin scripts, assume English
    return True


def filter_english_posts(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter list of posts to only include likely English content.
    
    Args:
        posts: List of posts to filter
        
    Returns:
        Filtered list containing only English posts
    """
    english_posts = []
    filtered_count = 0
    
    for post in posts:
        text = post.get('text', '')
        
        if is_likely_english(text):
            english_posts.append(post)
        else:
            filtered_count += 1
            logger.debug(f"Filtered non-English post: {text[:50]}...")
    
    if filtered_count > 0:
        logger.info(f"Filtered out {filtered_count} non-English posts, kept {len(english_posts)}")
    
    return english_posts
