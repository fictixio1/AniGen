# AniGen - Infinite Anime Director System

An episode-based infinite anime generation system using Google Veo 3.1 Fast and Claude Opus 4.5.

## Quick Start

### Option 1: Deploy to Railway (Recommended) ☁️

**Fastest way to get started - no local installation needed!**

1. Make sure you have Node.js installed (for Railway CLI)
2. Run the automated deployment script:

**Windows:**
```powershell
.\DEPLOY_NOW.bat
```

**Mac/Linux:**
```bash
chmod +x DEPLOY_NOW.sh
./DEPLOY_NOW.sh
```

That's it! Your system will be running in the cloud with:
- PostgreSQL database (hosted by Railway)
- Worker service (generates episodes)
- Web UI (public URL to view episodes)

**See [RAILWAY_QUICKSTART.md](RAILWAY_QUICKSTART.md) for detailed Railway deployment guide.**

**Cost:** ~$15-25/month for infrastructure + API costs

---

### Option 2: Local Development (Simple)

**For testing without dependencies:**

1. Install one dependency:
```powershell
python -m pip install aiosqlite
```

2. Run the ultra-simple version:
```powershell
python ultra_simple.py
```

This uses SQLite (no database server needed) and mock generation (no API keys needed).

**See [START_NOW.bat](START_NOW.bat) for one-click local setup.**

---

### Option 3: Full Local Setup (Advanced)

**For full development environment:**

Prerequisites:
- Python 3.11+
- PostgreSQL 15+
- Docker (optional)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy environment template:
```bash
cp .env.example .env
```

3. Edit `.env` with your database credentials

4. Start PostgreSQL (with Docker):
```bash
docker compose up -d postgres
```

Or use a local PostgreSQL installation and update `DATABASE_URL` in `.env`

5. The database schema will be automatically initialized on first connection.

6. Run the system:
```bash
python main.py
```

**See [SETUP.md](SETUP.md) for detailed local setup instructions.**

---

## Architecture

- **Director Model:** Claude Opus 4.5 (plans 6 scenes per episode)
- **Video Generator:** Google Veo 3.1 Fast (30s scenes with native audio)
- **Database:** PostgreSQL (canon state, episodes, scenes)
- **Storage:** AWS S3 (video files, character images)
- **Structure:** 6 scenes per episode (3 minutes total)
- **Schedule:** One scene every 10 minutes, one episode per hour

**Key Principle:** Single authority model - only Director makes narrative decisions. All other components are stateless tools.

## Cost

- **Per scene:** $4.61 (~$4.50 video + $0.10 director + $0.01 character)
- **Per episode:** $27.66 (6 scenes)
- **Per day:** ~$664 (24 episodes)
- **Per month:** ~$19,915 (720 episodes)
- **Infrastructure:** ~$15-25/month (Railway hosting)

## Usage

### Mock Mode (Testing)

Run the system in mock mode (no real API calls):

```bash
python main.py
```

This will generate mock episodes with 6 scenes each. In mock mode:
- Episodes are generated every 5 seconds (instead of 60 minutes)
- Video generation is instant
- No API costs

### Production Mode

1. Update `.env` and set:
```
GENERATION_MODE=real
```

2. Add your API keys:
```
ANTHROPIC_API_KEY=your_key_here
GOOGLE_AI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```

3. Configure AWS S3:
```
AWS_ACCESS_KEY_ID=your_key_here
AWS_SECRET_ACCESS_KEY=your_secret_here
AWS_S3_BUCKET=your-bucket-name
```

4. Run the system:
```bash
python main.py
```

The system will:
1. Plan episode with Director (6 scenes)
2. Generate scenes sequentially (one every 10 minutes)
3. Upload videos to S3
4. Update database with metadata
5. Repeat for next episode after 60 minutes

## Project Structure

```
anigen/
├── main.py                 # Orchestration loop
├── director.py             # Claude Opus wrapper (Phase 2)
├── canon.py                # Canon memory management
├── database.py             # PostgreSQL connection pool
├── episode_manager.py      # Episode lifecycle
├── config.py               # Configuration
├── generators/             # Video & character generation (Phase 3)
├── api/                    # FastAPI web interface (Phase 4)
├── schemas/                # Database & JSON schemas
└── tests/                  # Test suite
```

## Development Phases

- **Phase 1:** Core infrastructure with mock generation ✅ (Current)
- **Phase 2:** Director integration (Claude Opus)
- **Phase 3:** Asset generation (Veo 3.1, DALL-E)
- **Phase 4:** Web API + Test UI
- **Phase 5:** Production hardening

## Monitoring

View logs in real-time:
```bash
tail -f anigen.log
```

Query database for stats:
```sql
-- Total episodes generated
SELECT COUNT(*) FROM episodes WHERE generation_completed_at IS NOT NULL;

-- Total scenes
SELECT COUNT(*) FROM scenes;

-- Total cost
SELECT SUM(total_cost_usd) FROM episodes;

-- Recent episodes
SELECT episode_number, episode_arc_summary, total_cost_usd
FROM episodes
ORDER BY episode_number DESC
LIMIT 10;
```

## Graceful Shutdown

Press `Ctrl+C` to gracefully stop the system. It will:
1. Finish the current scene generation
2. Update database state
3. Close connections cleanly

## Architecture Principles

**Single Authority Rule:** Only the Director Model makes narrative decisions. All other components are stateless tools.

- Director owns canon
- Video generator is a pure renderer
- Character generator is on-demand only
- Canon memory updates only after successful generation

## License

Proprietary
