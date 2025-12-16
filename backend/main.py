"""
FastAPI Main Application

REST API for BoredPanda Content Sourcing Automation.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional
import logging
import os
from dotenv import load_dotenv
import asyncio

from backend.orchestration.scraper_orchestrator import ScraperOrchestrator
from backend.utils.cache import job_cache
from backend.utils.category_mapper import get_all_categories, get_all_platforms

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="BoredPanda Content Sourcing Automation",
    description="AI-powered content discovery system for viral stories",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Request/Response models
class ScrapeRequest(BaseModel):
    """Request model for scraping endpoint."""
    categories: List[str] = Field(..., description="List of categories to scrape")
    sources: List[str] = Field(..., description="List of sources to scrape")
    days_back: int = Field(7, ge=1, le=30, description="Days to look back (1-30)")


class ScrapeResponse(BaseModel):
    """Response model for scraping endpoint."""
    job_id: str
    status: str
    message: str


class ResultsResponse(BaseModel):
    """Response model for results endpoint."""
    status: str
    total_found: int
    top_stories: List[dict]
    job_id: str


# Initialize orchestrator
def get_orchestrator() -> ScraperOrchestrator:
    """Get scraper orchestrator instance."""
    apify_key = os.getenv("APIFY_API_TOKEN")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not apify_key or not openai_key:
        raise ValueError("Missing API keys. Check .env file.")
    
    return ScraperOrchestrator(apify_key, openai_key)


# Background task for scraping
async def run_scraping_job(
    job_id: str,
    categories: List[str],
    sources: List[str],
    days_back: int
):
    """
    Background task to run scraping workflow.
    
    Args:
        job_id: Job ID
        categories: Categories to scrape
        sources: Sources to scrape
        days_back: Days to look back
    """
    try:
        logger.info(f"Starting background job {job_id}")
        
        orchestrator = get_orchestrator()
        
        # Run workflow
        top_stories = await orchestrator.run_workflow(
            categories=categories,
            sources=sources,
            days_back=days_back,
            limit_per_source=20,
            top_n=20
        )
        
        # Update cache with results
        job_cache.update_job(job_id, top_stories, status="completed")
        
        logger.info(f"Job {job_id} completed: {len(top_stories)} stories")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        job_cache.update_job(job_id, [], status="failed")


# API Endpoints
@app.get("/")
async def root():
    """Serve frontend index page."""
    return FileResponse("frontend/index.html")


@app.get("/dashboard")
async def dashboard():
    """Serve frontend dashboard page."""
    return FileResponse("frontend/dashboard.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "BoredPanda Content Sourcing",
        "cache_stats": job_cache.get_stats()
    }


@app.get("/config")
async def get_config():
    """Get available categories and sources."""
    return {
        "categories": get_all_categories(),
        "sources": get_all_platforms()
    }


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Start a scraping job.
    
    Args:
        request: Scraping parameters
        background_tasks: FastAPI background tasks
        
    Returns:
        Job ID and status
    """
    try:
        # Validate inputs
        valid_categories = get_all_categories()
        valid_sources = get_all_platforms()
        
        invalid_cats = [c for c in request.categories if c not in valid_categories]
        invalid_srcs = [s for s in request.sources if s not in valid_sources]
        
        if invalid_cats:
            raise HTTPException(400, f"Invalid categories: {invalid_cats}")
        if invalid_srcs:
            raise HTTPException(400, f"Invalid sources: {invalid_srcs}")
        
        # Create job
        job_id = job_cache.create_job()
        
        # Add background task
        background_tasks.add_task(
            run_scraping_job,
            job_id,
            request.categories,
            request.sources,
            request.days_back
        )
        
        logger.info(f"Created job {job_id}: {len(request.categories)} categories, "
                   f"{len(request.sources)} sources")
        
        return ScrapeResponse(
            job_id=job_id,
            status="processing",
            message=f"Scraping {len(request.categories)} categories from {len(request.sources)} sources"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Scrape endpoint error: {e}")
        raise HTTPException(500, f" Internal server error: {str(e)}")


@app.get("/results/{job_id}", response_model=ResultsResponse)
async def get_results(job_id: str):
    """
    Get results for a scraping job.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job results
    """
    try:
        job = job_cache.get_job(job_id)
        
        if not job:
            raise HTTPException(404, "Job not found or expired")
        
        return ResultsResponse(
            status=job["status"],
            total_found=len(job["results"]),
            top_stories=job["results"],
            job_id=job_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Results endpoint error: {e}")
        raise HTTPException(500, f"Internal server error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
