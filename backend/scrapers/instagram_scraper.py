"""
Instagram Scraper

Uses Apify's apify/instagram-hashtag-scraper actor to fetch Instagram posts.
"""

from typing import List, Dict, Any
from apify_client import ApifyClient
import logging

logger = logging.getLogger(__name__)


class InstagramScraper:
    """Scraper for Instagram content using Apify."""
    
    def __init__(self, api_token: str):
        """
        Initialize Instagram scraper.
        
        Args:
            api_token: Apify API token
        """
        self.client = ApifyClient(api_token)
        self.actor_id = "apify/instagram-hashtag-scraper"
        logger.info("InstagramScraper initialized")
    
    async def scrape(
        self,
        hashtags: List[str],
        limit: int = 20,
        results_type: str = "posts"
    ) -> List[Dict[str, Any]]:
        """
        Scrape Instagram posts by hashtags.
        
        Args:
            hashtags: List of hashtags to search
            limit: Maximum results to return
            results_type: "posts" or "reels"
            
        Returns:
            List of Instagram posts
        """
        try:
            # Prepare input
            run_input = {
                "hashtags": hashtags[:5],  # Limit hashtags
                "resultsType": results_type,
                "resultsLimit": limit,
                "language": "en"  # English language preference
            }
            
            logger.info(f"Starting Instagram scrape: hashtags={hashtags}, limit={limit}")
            
            # Run the actor
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
                if len(results) >= limit:
                    break
            
            logger.info(f"Instagram scrape completed: {len(results)} posts")
            return results
            
        except Exception as e:
            logger.error(f"Instagram scraping error: {e}")
            return []
