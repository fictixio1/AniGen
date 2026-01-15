# Clean Setup: Vercel (Frontend) + Railway (Backend)

## Architecture

```
┌─────────────────────────────────────┐
│         VERCEL (Frontend)           │
│                                     │
│  - Next.js or static site           │
│  - Public domain/URL                │
│  - Fetches from Railway API         │
│  - Displays episodes                │
└──────────────┬──────────────────────┘
               │ HTTP requests
               ▼
┌─────────────────────────────────────┐
│       RAILWAY (Backend)             │
│                                     │
│  Service 1: FastAPI (API endpoints) │
│  Service 2: Worker (generator)      │
│  Service 3: PostgreSQL (database)   │
└─────────────────────────────────────┘
```

## Step 1: Railway Backend Setup

### Delete Current Railway Project
1. Go to https://railway.app/dashboard
2. Delete the broken project completely
3. Start fresh

### Create New Railway Project
1. Click "New Project"
2. Select "Empty Project"
3. Name it "AniGen Backend"

### Add PostgreSQL
1. Click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway creates database with `DATABASE_URL` automatically

### Add Worker Service
1. Click "+ New"
2. Select "GitHub Repo"
3. Choose "fictixio1/AniGen"
4. **Important:** Set custom start command in settings:
   - Go to Settings → Start Command
   - Enter: `python start_worker.py`

### Add API Service
1. Click "+ New" again
2. Select "GitHub Repo" → "fictixio1/AniGen" (same repo)
3. **Important:** Set custom start command:
   - Go to Settings → Start Command
   - Enter: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. Go to Settings → Generate Domain (for public API access)

### Configure Environment Variables

**For BOTH services (Worker + API), add these variables:**

```
DATABASE_URL = (automatically set by Railway when you link PostgreSQL)
GENERATION_MODE = mock
SCENES_PER_EPISODE = 6
SCENE_GENERATION_INTERVAL_MINUTES = 10
LOG_LEVEL = INFO
```

**Link PostgreSQL to services:**
1. Click on Worker service → Settings → "Add Service Reference"
2. Select PostgreSQL
3. Repeat for API service

## Step 2: Vercel Frontend Setup

### Option A: Next.js Frontend (Recommended)

I'll create a clean Next.js app that:
- Fetches episodes from Railway API
- Displays video grid
- Auto-refreshes
- SEO optimized

### Option B: Static HTML (Simpler)

Just HTML/CSS/JS that fetches from Railway API.

---

## Which setup do you want?

1. **Full Next.js** - Modern, fast, SEO-friendly, serverless
2. **Simple static site** - Just HTML/CSS/JS, very lightweight

Let me know and I'll create the complete setup for you.
