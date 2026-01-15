"""FastAPI application for AniGen web interface."""

import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import db
from api.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()


# Create FastAPI app
app = FastAPI(
    title="AniGen - Infinite Anime Director",
    description="Web interface for viewing generated anime episodes",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware to allow requests from Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (can restrict to Vercel domain later)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="api/static"), name="static")
templates = Jinja2Templates(directory="api/templates")

# Include API routes
app.include_router(router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Homepage - list of episodes."""
    episodes = await db.fetch("""
        SELECT
            e.*,
            COUNT(s.id) as scene_count,
            COUNT(CASE WHEN s.generation_completed_at IS NOT NULL THEN 1 END) as completed_scenes
        FROM episodes e
        LEFT JOIN scenes s ON s.episode_id = e.id
        GROUP BY e.id
        ORDER BY e.episode_number DESC
        LIMIT 20
    """)

    state = await db.fetchrow("SELECT * FROM series_state WHERE id = 1")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "episodes": episodes,
        "state": state
    })


@app.get("/episode/{episode_number}", response_class=HTMLResponse)
async def episode_detail(request: Request, episode_number: int):
    """Episode detail page - view all 6 scenes."""
    episode = await db.fetchrow("""
        SELECT * FROM episodes WHERE episode_number = $1
    """, episode_number)

    if not episode:
        return HTMLResponse("Episode not found", status_code=404)

    scenes = await db.fetch("""
        SELECT * FROM scenes
        WHERE episode_id = $1
        ORDER BY scene_in_episode ASC
    """, episode["id"])

    return templates.TemplateResponse("episode.html", {
        "request": request,
        "episode": episode,
        "scenes": scenes
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
