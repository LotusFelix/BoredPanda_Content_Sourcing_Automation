"""
Virality Scoring Engine

Hybrid scoring system using rule-based metrics + LLM enhancement.
"""

from typing import List, Dict, Any
from datetime import datetime
import logging
import json
import os
from openai import OpenAI

logger = logging.getLogger(__name__)


class ViralityScorer:
    """Calculates virality scores for social media posts."""
    
    def __init__(self, openai_api_key: str):
        """
        Initialize scoring engine.
        
        Args:
            openai_api_key: OpenAI API key for LLM enhancement
        """
        self.client = OpenAI(api_key=openai_api_key)
        logger.info("ViralityScorer initialized")
    
    def calculate_velocity_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate velocity score (engagements per hour).
        Max 25 points.
        """
        try:
            # Parse timestamp
            timestamp_str = post.get("timestamp", "")
            if isinstance(timestamp_str, str):
                # Try parsing ISO format
                try:
                    post_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except:
                    post_time = datetime.now()
            else:
                post_time = datetime.now()
            
            hours_since_post = max((datetime.now(post_time.tzinfo) - post_time).total_seconds() / 3600, 0.1)
            
            # Calculate total engagements
            engagements = (
                post.get("likes", 0) +
                post.get("shares", 0) +
                post.get("comments", 0)
            )
            
            velocity = engagements / hours_since_post
            
            # Normalize to 0-25 scale (1000+ engagements/hour = max score)
            score = min(25, (velocity / 1000) * 25)
            return round(score, 2)
            
        except Exception as e:
            logger.error(f"Error calculating velocity score: {e}")
            return 0.0
    
    def calculate_volume_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate volume score (total engagements).
        Max 20 points.
        """
        total_engagements = (
            post.get("likes", 0) +
            post.get("shares", 0) +
            post.get("comments", 0)
        )
        
        # Normalize to 0-20 scale (100k+ engagements = max score)
        score = min(20, (total_engagements / 100000) * 20)
        return round(score, 2)
    
    def calculate_engagement_rate_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate engagement rate score.
        Max 20 points.
        """
        followers = post.get("author_followers", 0)
        if followers == 0:
            return 0.0
        
        total_engagements = (
            post.get("likes", 0) +
            post.get("shares", 0) +
            post.get("comments", 0)
        )
        
        engagement_rate = (total_engagements / followers) * 100
        
        # Normalize to 0-20 scale (10%+ engagement rate = max score)
        score = min(20, (engagement_rate / 10) * 20)
        return round(score, 2)
    
    def calculate_diversity_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate diversity score (placeholder).
        Max 15 points.
        """
        # For prototype, give flat score
        # In production, check if story appears across multiple platforms
        return 10.0
    
    def calculate_novelty_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate novelty score (placeholder).
        Max 10 points.
        """
        # For prototype, give flat score
        # In production, check against historical data
        return 7.0
    
    def calculate_authority_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate authority score.
        Max 10 points.
        """
        followers = post.get("author_followers", 0)
        
        # Give bonus points based on follower count
        if followers > 1000000:  # 1M+ followers
            return 10.0
        elif followers > 100000:  # 100K+ followers
            return 7.0
        elif followers > 10000:  # 10K+ followers
            return 5.0
        else:
            return 3.0
    
    def calculate_base_score(self, post: Dict[str, Any]) -> float:
        """
        Calculate total base score using rule-based metrics.
        
        Returns:
            Score from 0-100
        """
        velocity = self.calculate_velocity_score(post)
        volume = self.calculate_volume_score(post)
        engagement_rate = self.calculate_engagement_rate_score(post)
        diversity = self.calculate_diversity_score(post)
        novelty = self.calculate_novelty_score(post)
        authority = self.calculate_authority_score(post)
        
        total = velocity + volume + engagement_rate + diversity + novelty + authority
        
        logger.debug(f"Base score breakdown: v={velocity}, vol={volume}, eng={engagement_rate}, "
                    f"div={diversity}, nov={novelty}, auth={authority}, total={total}")
        
        return round(total, 2)
    
    def enhance_with_llm(self, post: Dict[str, Any], base_score: float) -> Dict[str, Any]:
        """
        Use GPT-4o-mini to generate editorial brief and adjust score.
        
        Args:
            post: Post with base score
            base_score: Rule-based score
            
        Returns:
            Enhanced post with AI brief and final score
        """
        try:
            prompt = f"""
You are a content analyst for BoredPanda, a viral entertainment publisher focused on 
Creativity, Quality, Inclusivity, and Community values.

Analyze this social media post:

Platform: {post['platform']}
Content: {post['text'][:500]}
Engagement: {post['likes']} likes, {post['shares']} shares, {post['comments']} comments
Author: {post['author']} ({post['author_followers']} followers)

Current virality score: {base_score}/100

Your tasks:

1. **Virality Analysis** (2-3 sentences):
   - WHY is this going viral? (emotional hooks, timing, relatability, novelty)
   - What makes it shareable and engaging?

2. **BoredPanda Alignment** (2-3 sentences):
   - Why would this resonate with BoredPanda's audience?
   - How does it align with our values (Creativity/Quality/Inclusivity/Community)?
   - What's the uplifting or thought-provoking angle?

3. **Writer Guidance** (3-5 actionable bullet points):
   - Story angle/headline suggestions
   - Key quotes or moments to highlight
   - Additional research needed (background, context, verification)
   - Potential interview sources (creator, experts, audience)
   - Visual storytelling opportunities (screenshots, video embeds, before/after)
   - Recommended article structure (listicle vs narrative vs interview format)

4. **Score Adjustment** (-10 to +10):
   Based on:
   - Emotional appeal (awe, joy, surprise, curiosity)
   - Visual storytelling potential
   - Shareability and "social currency"
   - Alignment with BoredPanda values
   - Timeliness and cultural relevance

Respond ONLY with valid JSON (no markdown):
{{
    "virality_brief": "Why this is going viral...",
    "boredpanda_fit": "Why this resonates with our audience...",
    "writer_guidance": [
        "Headline suggestion: ...",
        "Key angle: ...",
        "Research needed: ...",
        "Visual opportunities: ...",
        "Recommended format: ..."
    ],
    "score_adjustment": -5,
    "adjustment_reasoning": "Brief explanation of score change"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            final_score = min(100, max(0, base_score + result.get('score_adjustment', 0)))
            
            # Combine briefs into comprehensive AI brief
            full_brief = f"""**Why It's Viral:** {result['virality_brief']}

**BoredPanda Fit:** {result['boredpanda_fit']}

**Writer's Roadmap:**
{chr(10).join(f"• {tip}" for tip in result.get('writer_guidance', []))}
"""
            
            return {
                **post,
                "virality_score": round(final_score, 2),
                "ai_brief": full_brief,
                "virality_analysis": result.get('virality_brief', ''),
                "boredpanda_alignment": result.get('boredpanda_fit', ''),
                "writer_tips": result.get('writer_guidance', []),
                "score_reasoning": result.get('adjustment_reasoning', '')
            }
            
        except Exception as e:
            logger.error(f"LLM enhancement error: {e}")
            # Fallback to rule-based only
            return {
                **post,
                "virality_score": round(base_score, 2),
                "ai_brief": "AI enhancement unavailable. Scored using rule-based metrics only.",
                "virality_analysis": "",
                "boredpanda_alignment": "",
                "writer_tips": [],
                "score_reasoning": "LLM error"
            }
    
    def score_posts(self, posts: List[Dict[str, Any]], use_llm: bool = True) -> List[Dict[str, Any]]:
        """
        Score a list of posts.
        
        Args:
            posts: List of normalized posts
            use_llm: Whether to use LLM enhancement (default: True)
            
        Returns:
            List of scored posts
        """
        scored_posts = []
        
        # Calculate base scores for all posts
        for post in posts:
            base_score = self.calculate_base_score(post)
            post['base_score'] = base_score
        
        # Sort by base score and select top 30 for LLM enhancement
        posts_sorted = sorted(posts, key=lambda x: x['base_score'], reverse=True)
        top_posts = posts_sorted[:30] if use_llm else []
        remaining_posts = posts_sorted[30:] if use_llm else posts_sorted
        
        # Enhance top posts with LLM
        if use_llm and top_posts:
            logger.info(f"Enhancing top {len(top_posts)} posts with LLM")
            for post in top_posts:
                enhanced = self.enhance_with_llm(post, post['base_score'])
                scored_posts.append(enhanced)
        
        # Add remaining posts with base score only
        for post in remaining_posts:
            scored_posts.append({
                **post,
                "virality_score": round(post['base_score'], 2),
                "ai_brief": "Rule-based scoring only (not in top 30).",
                "virality_analysis": "",
                "boredpanda_alignment": "",
                "writer_tips": [],
                "score_reasoning": "Below LLM threshold"
            })
        
        logger.info(f"Scored {len(scored_posts)} posts")
        return scored_posts
