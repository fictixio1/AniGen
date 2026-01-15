# AniGen Setup Guide

## Quick Start (Windows)

### 1. Install Prerequisites

**Install Python 3.11+:**
```powershell
# Download from https://www.python.org/downloads/
# Or use winget:
winget install Python.Python.3.11
```

**Install PostgreSQL:**
```powershell
# Download from https://www.postgresql.org/download/windows/
# Or use chocolatey:
choco install postgresql
```

**Install Docker Desktop (Optional):**
```powershell
# Download from https://www.docker.com/products/docker-desktop
# Or use winget:
winget install Docker.DockerDesktop
```

### 2. Setup Database

**Option A: Using Docker (Easiest)**
```powershell
cd C:\Users\klent\OneDrive\Documents\CODE\AniGen
docker compose up -d postgres
```

**Option B: Using Local PostgreSQL**
```powershell
# Open PostgreSQL command line (psql)
psql -U postgres

# Create database and user
CREATE DATABASE anigen;
CREATE USER anigen_user WITH PASSWORD 'anigen_password';
GRANT ALL PRIVILEGES ON DATABASE anigen TO anigen_user;
\q

# Initialize schema
psql -U anigen_user -d anigen -f schemas/database_schema.sql
```

### 3. Install Python Dependencies

```powershell
cd C:\Users\klent\OneDrive\Documents\CODE\AniGen
python -m pip install -r requirements.txt
```

### 4. Run the System

**Mock Mode (No API Keys Required):**
```powershell
python main.py
```

You should see output like:
```
2026-01-15 10:00:00 - __main__ - INFO - AniGen Orchestrator Starting...
2026-01-15 10:00:00 - __main__ - INFO - Mode: mock
2026-01-15 10:00:00 - __main__ - INFO - Scenes per episode: 6
============================================================
Starting Episode 1
============================================================
2026-01-15 10:00:01 - __main__ - INFO - Director planning episode 1

Generating Scene 1/6 (Global #1)
2026-01-15 10:00:01 - __main__ - INFO - Generating 30s video...
✓ Scene 1 completed: mock://video/1736938801.123.mp4
...
```

**Stop the system:** Press `Ctrl+C` for graceful shutdown

### 5. Verify It's Working

**Open another terminal and check the database:**
```powershell
psql -U anigen_user -d anigen
```

```sql
-- Check episodes generated
SELECT episode_number, episode_arc_summary, total_cost_usd, generation_completed_at
FROM episodes
ORDER BY episode_number DESC
LIMIT 5;

-- Check total scenes
SELECT COUNT(*) as total_scenes FROM scenes;

-- Check series state
SELECT * FROM series_state;
```

## Troubleshooting

### Database Connection Errors

**Error:** `could not connect to server`

**Solution:**
1. Check PostgreSQL is running:
   ```powershell
   # For Docker
   docker ps | grep postgres

   # For local PostgreSQL (Windows services)
   Get-Service postgresql*
   ```

2. Verify `.env` has correct DATABASE_URL:
   ```
   DATABASE_URL=postgresql://anigen_user:anigen_password@localhost:5432/anigen
   ```

3. Test connection manually:
   ```powershell
   psql -U anigen_user -d anigen -h localhost
   ```

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'asyncpg'`

**Solution:**
```powershell
python -m pip install asyncpg
# Or reinstall all dependencies
python -m pip install -r requirements.txt
```

### Port Already in Use

**Error:** `port 5432 is already allocated`

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :5432

# Stop the process or change the port in docker-compose.yml
ports:
  - "5433:5432"  # Change host port to 5433

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://anigen_user:anigen_password@localhost:5433/anigen
```

## What to Expect

### Mock Mode Behavior

- **Episodes generated:** One every 5 seconds (fast for testing)
- **Scenes per episode:** 6 (each 30 seconds)
- **Video generation:** Instant simulation
- **Database updates:** Real-time
- **Costs tracked:** Mock costs ($27.66 per episode)
- **No API calls:** Everything is simulated

### Production Mode (Phase 3+)

- **Episodes generated:** One every 60 minutes
- **Scene interval:** 10 minutes between scenes
- **Video generation:** Real Veo 3.1 API calls (~30s per scene)
- **Real costs:** ~$27.66 per episode
- **Requires:** API keys for Claude Opus, Veo 3.1, DALL-E 3

## Next Steps

Once the system is running successfully in mock mode:

1. **Build Web UI** (Phase 4) - View episodes in browser
2. **Integrate Director** (Phase 2) - Real Claude Opus planning
3. **Add Video Generation** (Phase 3) - Real Veo 3.1 videos
4. **Deploy to Production** - Run 24/7

## Performance Expectations

### Mock Mode
- Memory usage: ~100-200MB
- CPU usage: <5%
- Database size: ~1MB per 100 episodes
- Can generate 720 episodes/hour (testing)

### Production Mode
- Memory usage: ~200-500MB
- CPU usage: ~10-20%
- Database size: ~1MB per 100 episodes
- Network: ~50MB down per scene (video download)
- Generates 24 episodes/day (infinite)

## Database Maintenance

### Backup Database
```powershell
pg_dump -U anigen_user -d anigen > backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

### Restore Database
```powershell
psql -U anigen_user -d anigen < backup_20260115_120000.sql
```

### View Logs
```sql
-- Recent errors
SELECT * FROM generation_logs
WHERE log_level = 'ERROR'
ORDER BY created_at DESC
LIMIT 10;

-- Cost tracking
SELECT
    DATE(created_at) as date,
    COUNT(*) as episodes,
    SUM(total_cost_usd) as total_cost
FROM episodes
WHERE generation_completed_at IS NOT NULL
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

## Support

- Architecture docs: See plan file at `~/.claude/plans/tender-swimming-kurzweil.md`
- Issues: Check logs in database `generation_logs` table
- Database schema: `schemas/database_schema.sql`
