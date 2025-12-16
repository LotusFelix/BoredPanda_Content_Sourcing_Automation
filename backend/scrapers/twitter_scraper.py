"""
Twitter Scraper

Uses Apify's apidojo/tweet-scraper actor to fetch tweets.
"""

from typing import List, Dict, Any
from apify_client import ApifyClient
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class TwitterScraper:
    """Scraper for Twitter content using Apify."""
    
    def __init__(self, api_token: str):
        """
        Initialize Twitter scraper.
        
        Args:
            api_token: Apify API token
        """
        self.client = ApifyClient(api_token)
        self.actor_id = "apidojo/tweet-scraper"
        logger.info("TwitterScraper initialized")
    
    async def scrape(
        self,
        keywords: List[str],
        limit: int = 20,
        days_back: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Scrape tweets by keywords.
        
        Args:
            keywords: List of search keywords/hashtags
            limit: Maximum results to return
            days_back: How many days back to search
            
        Returns:
            List of tweets
        """
        try:
            # Calculate date range
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            # Build search terms with date filter
            search_terms = [
                f"{keyword} since:{start_date}"
                for keyword in keywords[:5]  # Limit to 5 keywords
            ]
            
            # Prepare input
            run_input = {
                "searchTerms": search_terms,
                "maxItems": limit,
                "sort": "Latest",
                "tweetLanguage": "en"
            }
            
            logger.info(f"Starting Twitter scrape: keywords={keywords}, limit={limit}")
            
            # Run the actor
            run = self.client.actor(self.actor_id).call(run_input=run_input)
            
            # Fetch results
            results = []
            for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                results.append(item)
                if len(results) >= limit:
                    break
            
            logger.info(f"Twitter scrape completed: {len(results)} posts")
            return results
            
        except Exception as e:
            logger.error(f"Twitter scraping error: {e}")
            return []
