"""
Facebook Scraper

Uses Apify's apify/facebook-posts-scraper actor to fetch Facebook posts.
"""

from typing import List, Dict, Any
from apify_client import ApifyClient
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FacebookScraper:
    """Scraper for Facebook content using Apify."""
    
    def __init__(self, api_token: str):
        """
        Initialize Facebook scraper.
        
        Args:
            api_token: Apify API token
        """
        self.client = ApifyClient(api_token)
        self.actor_id = "apify/facebook-posts-scraper"
        logger.info("FacebookScraper initialized")
    
    async def scrape(
        self,
        keywords: List[str],
        limit: int = 20,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Scrape Facebook posts by keywords.
        
        Args:
            keywords: List of search keywords
            limit: Maximum results to return  
            days_back: How many days back to search
            
        Returns:
            List of Facebook posts
        """
        try:
            # Construct search URLs
            search_urls = [
                f"https://www.facebook.com/search/posts/?q={keyword}"
                for keyword in keywords[:3]  # Limit to 3 keywords
            ]
            
            # Prepare input
            run_input = {
                "startUrls": [{"url": url} for url in search_urls],
                "resultsLimit": limit,
                "onlyPostsNewerThan": f"{days_back} days",
                "language": "en"  # English language only
            }
            
            logger.info(f"Starting Facebook scrape: keywords={keywords}, limit={limit}")
            
            # Run the actor
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
                if len(results) >= limit:
                    break
            
            logger.info(f"Facebook scrape completed: {len(results)} posts")
            return results
            
        except Exception as e:
            logger.error(f"Facebook scraping error: {e}")
            return []
