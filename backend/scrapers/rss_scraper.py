"""
RSS Feed Scraper

Uses Apify's jupri/rss-xml-scraper actor to fetch RSS feed content.
"""

from typing import List, Dict, Any
from apify_client import ApifyClient
import logging

logger = logging.getLogger(__name__)


class RSSScraper:
    """Scraper for RSS feeds using Apify."""
    
    def __init__(self, api_token: str):
        """
        Initialize RSS scraper.
        
        Args:
            api_token: Apify API token
        """
        self.client = ApifyClient(api_token)
        self.actor_id = "jupri/rss-xml-scraper"
        logger.info("RSSScraper initialized")
    
    async def scrape(
        self,
        feed_urls: List[str],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Scrape RSS feeds.
        
        Args:
            feed_urls: List of RSS feed URLs
            limit: Maximum results per feed
            
        Returns:
            List of RSS items
        """
        all_results = []
        
        try:
            for feed_url in feed_urls[:3]:  # Limit to 3 feeds
                try:
                    # Prepare input
                    run_input = {
                        "url": feed_url,
                        "dev_dataset_clear": True
                    }
                    
                    logger.info(f"Scraping RSS feed: {feed_url}")
                    
                    # Run the actor
                    run = self.client.actor(self.actor_id).call(run_input=run_input)
                    
                    # Fetch results
                    results = []
                    for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
                        results.append(item)
                        if len(results) >= limit:
                            break
                    
                    all_results.extend(results)
                    logger.info(f"RSS feed scraped: {len(results)} items from {feed_url}")
                    
                except Exception as e:
                    logger.error(f"Error scraping feed {feed_url}: {e}")
                    continue
            
            logger.info(f"RSS scrape completed: {len(all_results)} total items")
            return all_results
            
        except Exception as e:
            logger.error(f"RSS scraping error: {e}")
            return []
