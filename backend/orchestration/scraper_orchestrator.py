"""
Scraper Orchestrator

Coordinates parallel scraping across multiple platforms.
"""

import asyncio
from typing import List, Dict, Any
import logging
import os

from backend.scrapers.tiktok_scraper import TikTokScraper
from backend.scrapers.instagram_scraper import InstagramScraper
from backend.scrapers.facebook_scraper import FacebookScraper
from backend.scrapers.twitter_scraper import TwitterScraper
from backend.scrapers.rss_scraper import RSSScraper
from backend.utils.category_mapper import get_hashtags, get_rss_feeds
from backend.utils.aggregator import normalize_schema, deduplicate_results, rank_by_score, get_top_n
from backend.scoring.virality_scorer import ViralityScorer
from backend.utils.language_filter import filter_english_posts

logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    """Orchestrates parallel scraping and scoring across platforms."""
    
    def __init__(self, apify_api_key: str, openai_api_key: str):
        """
        Initialize orchestrator.
        
        Args:
            apify_api_key: Apify API token
            openai_api_key: OpenAI API key
        """
        self.tiktok = TikTokScraper(apify_api_key)
        self.instagram = InstagramScraper(apify_api_key)
        self.facebook = FacebookScraper(apify_api_key)
        self.twitter = TwitterScraper(apify_api_key)
        self.rss = RSSScraper(apify_api_key)
        self.scorer = ViralityScorer(openai_api_key)
        
        logger.info("ScraperOrchestrator initialized with all 5 scrapers")
    
    async def scrape_source(
        self,
        source: str,
        category: str,
        limit: int,
        days_back: int
    ) -> List[Dict[str, Any]]:
        """
        Scrape a single source for a category.
        
        Args:
            source: Platform name
            category: Content category
            limit: Max results
            days_back: Days to look back
            
        Returns:
            List of scraped posts
        """
        try:
            logger.info(f"Scraping {source} for category: {category}")
            
            if source == "TikTok":
                hashtags = get_hashtags(category, "TikTok")
                results = await self.tiktok.scrape(hashtags, limit, days_back)
                
            elif source == "Instagram":
                hashtags = get_hashtags(category, "Instagram")
                results = await self.instagram.scrape(hashtags, limit)
                
            elif source == "Facebook":
                keywords = get_hashtags(category, "Facebook")
                results = await self.facebook.scrape(keywords, limit, days_back)
                
            elif source == "Twitter":
                keywords = get_hashtags(category, "Twitter")
                results = await self.twitter.scrape(keywords, limit, days_back)
                
            elif source == "RSS":
                feed_urls = get_rss_feeds(category)
                if not feed_urls:
                    logger.warning(f"No RSS feeds configured for category: {category}")
                    return []
                results = await self.rss.scrape(feed_urls, limit)
                
            else:
                logger.warning(f"Unknown source: {source}")
                return []
            
            # Normalize results
            normalized = normalize_schema(results, source)
            
            # Filter for English language only
            english_only = filter_english_posts(normalized)
            
            # Add category tag to each post
            for post in english_only:
                post['category'] = category
            
            logger.info(f"Scraped {len(english_only)} English posts from {source}/{category}")
            return english_only
            
        except Exception as e:
            logger.error(f"Error scraping {source}/{category}: {e}")
            return []
    
    async def scrape_all(
        self,
        categories: List[str],
        sources: List[str],
        days_back: int = 7,
        limit_per_source: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Scrape all combinations of categories and sources in parallel.
        
        Args:
            categories: List of categories to scrape
            sources: List of sources to scrape
            days_back: Days to look back
            limit_per_source: Max results per source/category combo
            
        Returns:
            List of all scraped and normalized posts
        """
        tasks = []
        
        # Create tasks for each category/source combination
        for category in categories:
            for source in sources:
                task = self.scrape_source(source, category, limit_per_source, days_back)
                tasks.append(task)
        
        logger.info(f"Starting {len(tasks)} parallel scraping tasks")
        
        # Execute all tasks in parallel with timeout
        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in parallel scraping: {e}")
            results = []
        
        # Flatten results and filter out errors
        all_posts = []
        for result in results:
            if isinstance(result, list):
                all_posts.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Scraping task failed: {result}")
        
        logger.info(f"Total posts scraped: {len(all_posts)}")
        return all_posts
    
    async def score_and_rank(
        self,
        posts: List[Dict[str, Any]],
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Score posts and return top N.
        
        Args:
            posts: List of posts to score
            top_n: Number of top posts to return
            
        Returns:
            Top N scored posts
        """
        if not posts:
            logger.warning("No posts to score")
            return []
        
        # Deduplicate
        unique_posts = deduplicate_results(posts)
        
        # Score all posts
        scored_posts = self.scorer.score_posts(unique_posts, use_llm=True)
        
        # Rank by score
        ranked_posts = rank_by_score(scored_posts)
        
        # Get top N
        top_posts = get_top_n(ranked_posts, top_n)
        
        logger.info(f"Returning top {len(top_posts)} posts")
        return top_posts
    
    async def run_workflow(
        self,
        categories: List[str],
        sources: List[str],
        days_back: int = 7,
        limit_per_source: int = 20,
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Run complete scraping and scoring workflow.
        
        Args:
            categories: Categories to scrape
            sources: Sources to scrape
            days_back: Days to look back
            limit_per_source: Max results per source
            top_n: Number of top stories to return
            
        Returns:
            Top N scored stories
        """
        logger.info(f"Starting workflow: {len(categories)} categories × {len(sources)} sources")
        
        # Phase 1: Scrape all sources
        all_posts = await self.scrape_all(categories, sources, days_back, limit_per_source)
        
        if not all_posts:
            logger.warning("No posts found in scraping phase")
            return []
        
        # Phase 2: Score and rank
        top_stories = await self.score_and_rank(all_posts, top_n)
        
        logger.info(f"Workflow complete: {len(top_stories)} top stories")
        return top_stories
