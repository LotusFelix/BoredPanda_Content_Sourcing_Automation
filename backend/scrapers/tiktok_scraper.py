"""
TikTok Scraper

Uses Apify's clockworks/tiktok-scraper actor to fetch TikTok posts.
"""

from typing import List, Dict, Any
from apify_client import ApifyClient
import os
import logging

logger = logging.getLogger(__name__)


class TikTokScraper:
    """Scraper for TikTok content using Apify."""
    
    def __init__(self, api_token: str):
        """
        Initialize TikTok scraper.
        
        Args:
            api_token: Apify API token
        """
        self.client = ApifyClient(api_token)
        self.actor_id = "GdWCkxBtKWOsKjdch"  # clockworks/tiktok-scraper
        logger.info("TikTokScraper initialized")
    
    async def scrape(
        self,
        hashtags: List[str],
        limit: int = 20,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Scrape TikTok posts by hashtags.
        
        Args:
            hashtags: List of hashtags to search (max 5 recommended)
            limit: Maximum results to return
            days_back: How many days back to search
            
        Returns:
            List of TikTok posts
        """
        try:
            # Prepare input
            run_input = {
                "hashtags": hashtags[:5],  # Limit to 5 hashtags for cost control
                "resultsPerPage": limit,
                "profileSorting": "latest",
                "shouldDownloadVideos": False,  # Don't download videos (save bandwidth)
                "shouldDownloadCovers": True,  # Get thumbnails
                "commentsPerPost": 0,  # Don't fetch comments
                "proxyCountryCode": "None",
                "lang": "en"  # English language only
            }
            
            logger.info(f"Starting TikTok scrape: hashtags={hashtags}, limit={limit}")
            
            # Run the actor
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
                if len(results) >= limit:
                    break
            
            logger.info(f"TikTok scrape completed: {len(results)} posts")
            return results
            
        except Exception as e:
            logger.error(f"TikTok scraping error: {e}")
            return []
