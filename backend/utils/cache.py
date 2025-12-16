"""
In-Memory Job Cache

Stores scraping job results temporarily with TTL-based cleanup.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class JobCache:
    """In-memory cache for storing job results with TTL."""
    
    def __init__(self, ttl_minutes: int = 60):
        """
        Initialize job cache.
        
        Args:
            ttl_minutes: Time-to-live for jobs in minutes
        """
        self.jobs: Dict[str, Dict[str, Any]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
        logger.info(f"JobCache initialized with TTL={ttl_minutes} minutes")
    
    def create_job(self, job_id: Optional[str] = None) -> str:
        """
        Create a new job entry.
        
        Args:
            job_id: Optional custom job ID (generates UUID if not provided)
            
        Returns:
            Job ID
        """
        if not job_id:
            job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "status": "processing",
            "results": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        logger.info(f"Created job: {job_id}")
        return job_id
    
    def update_job(self, job_id: str, results: list, status: str = "completed"):
        """
        Update job with results.
        
        Args:
            job_id: Job ID to update
            results: List of story results
            status: Job status ("completed", "failed", etc.)
        """
        if job_id not in self.jobs:
            logger.warning(f"Attempted to update non-existent job: {job_id}")
            return
        
        self.jobs[job_id]["results"] = results
        self.jobs[job_id]["status"] = status
        self.jobs[job_id]["updated_at"] = datetime.now()
        
        logger.info(f"Updated job {job_id}: {len(results)} results, status={status}")
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID to retrieve
            
        Returns:
            Job data or None if not found
        """
        self._cleanup_expired()
        
        if job_id not in self.jobs:
            logger.warning(f"Job not found: {job_id}")
            return None
        
        return self.jobs[job_id]
    
    def delete_job(self, job_id: str):
        """Delete a job from cache."""
        if job_id in self.jobs:
            del self.jobs[job_id]
            logger.info(f"Deleted job: {job_id}")
    
    def _cleanup_expired(self):
        """Remove expired jobs based on TTL."""
        now = datetime.now()
        expired_jobs = [
            job_id for job_id, job in self.jobs.items()
            if now - job['created_at'] > self.ttl
        ]
        
        for job_id in expired_jobs:
            del self.jobs[job_id]
        
        if expired_jobs:
            logger.info(f"Cleaned up {len(expired_jobs)} expired jobs")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        self._cleanup_expired()
        return {
            "total_jobs": len(self.jobs),
            "processing": sum(1 for j in self.jobs.values() if j["status"] == "processing"),
            "completed": sum(1 for j in self.jobs.values() if j["status"] == "completed"),
            "failed": sum(1 for j in self.jobs.values() if j["status"] == "failed")
        }


# Global cache instance
job_cache = JobCache(ttl_minutes=60)
