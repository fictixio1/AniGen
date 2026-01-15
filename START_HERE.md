# 🚀 START HERE - AniGen Quick Start

## What You Have

A complete **Infinite Anime Director** system that generates 3-minute episodes (6 scenes × 30s) continuously.

**Current Status:** ✅ **Ready to Run** (Phases 1 & 4 Complete)

## One Command to Rule Them All

```powershell
# Windows PowerShell
cd C:\Users\klent\OneDrive\Documents\CODE\AniGen
.\setup.ps1
```

This will:
1. ✅ Check Python & PostgreSQL
2. ✅ Install all dependencies
3. ✅ Set up database
4. ✅ Configure environment

Then run:
```powershell
python run_with_ui.py
```

**That's it!** Open http://localhost:8000 in your browser.

---

## What You'll See

### In Terminal:
```
============================================================
  AniGen - Starting System with Web UI
============================================================

Starting components:
  [1] Orchestrator (episode generation)
  [2] Web UI (http://localhost:8000)

✓ Orchestrator started
✓ Web UI started at http://localhost:8000

============================================================
  System Running!
============================================================

🌐 Open your browser: http://localhost:8000
📊 Episodes will appear as they're generated
⚡ Mock mode: New episode every 5 seconds

Logs:
------------------------------------------------------------
[ORCHESTRATOR] ============================================================
[ORCHESTRATOR] Starting Episode 1
[ORCHESTRATOR] ============================================================
[ORCHESTRATOR] Director planning episode 1
[ORCHESTRATOR] Generating Scene 1/6 (Global #1)
[ORCHESTRATOR] ✓ Scene 1 completed: mock://video/1736938801.mp4
...
```

### In Browser (http://localhost:8000):
- **Homepage:** List of all generated episodes
- **Episode pages:** View all 6 scenes with metadata
- **Auto-refresh:** Updates every 10 minutes
- **Statistics:** Total episodes, scenes, duration, cost

---

## Current Features (Phase 1 & 4)

✅ **Episode Generation**
- Director plans 6 scenes per episode
- One episode every 5 seconds (mock mode)
- Full database tracking

✅ **Web Interface**
- Beautiful dark-mode UI
- Episode list with status
- Scene-by-scene viewing
- Auto-refresh
- Cost tracking

✅ **Database**
- PostgreSQL with full schema
- Episodes, scenes, characters
- System state tracking
- Generation logs

---

## Coming Soon (Phases 2-3)

🔜 **Phase 2:** Claude Opus Director
- Real AI episode planning
- Narrative coherence
- Character management

🔜 **Phase 3:** Veo 3.1 Video Generation
- Real 30s video generation
- Native audio support
- AWS S3 storage

---

## File Structure

```
AniGen/
├── START_HERE.md           ← You are here
├── QUICKSTART.md           ← Quick reference
├── README.md               ← Full documentation
├── SETUP.md                ← Detailed setup guide
│
├── run_with_ui.py          ← Run everything (orchestrator + web UI)
├── main.py                 ← Orchestrator only
├── setup.ps1               ← Automated setup (Windows)
├── setup.sh                ← Automated setup (Linux/Mac)
│
├── config.py               ← Configuration
├── database.py             ← Database connection
├── canon.py                ← Canon memory
├── episode_manager.py      ← Episode lifecycle
│
├── api/
│   ├── main.py             ← FastAPI app
│   ├── routes.py           ← API endpoints
│   ├── templates/          ← HTML pages
│   └── static/             ← CSS styles
│
└── schemas/
    └── database_schema.sql ← Database structure
```

---

## Common Commands

| Task | Command |
|------|---------|
| **Setup** | `.\setup.ps1` |
| **Run everything** | `python run_with_ui.py` |
| **Run orchestrator only** | `python main.py` |
| **Run web UI only** | `uvicorn api.main:app --reload` |
| **Stop** | Press `Ctrl+C` |
| **Check database** | `psql -U anigen_user -d anigen` |
| **View episodes** | Open http://localhost:8000 |

---

## Troubleshooting

### "Python not found"
Download from https://www.python.org/downloads/ and install

### "Docker/PostgreSQL not found"
Install one of:
- Docker Desktop: https://www.docker.com/products/docker-desktop
- PostgreSQL: https://www.postgresql.org/download/

### "Can't connect to database"
```powershell
# Check if running
docker ps | grep postgres

# Restart if needed
docker compose restart postgres
```

### "Port 8000 already in use"
```powershell
# Kill whatever's using it
netstat -ano | findstr :8000
# Or change port in run_with_ui.py
```

---

## Cost Breakdown

### Mock Mode (Current)
- **Cost:** $0 (simulated)
- **Speed:** 1 episode every 5 seconds
- **Purpose:** Testing

### Production Mode (Phase 3)
- **Cost:** $27.66 per episode
- **Speed:** 1 episode per hour (60 minutes)
- **Daily:** ~$664 (24 episodes)
- **Monthly:** ~$19,915 (720 episodes)

**Breakdown per episode:**
- Veo 3.1 video (6 scenes): $27.00
- Claude Opus director: $0.60
- DALL-E characters: $0.06

---

## Architecture Principles

**Single Authority Rule:** Only the Director Model makes narrative decisions.

- ✅ Director owns canon
- ✅ Video generator is stateless
- ✅ Character generator is on-demand only
- ✅ Canon updates only after success

---

## Next Steps

Once you have it running:

1. **Watch it generate episodes** in the terminal
2. **Open the Web UI** at http://localhost:8000
3. **Check the database** to see episodes stored
4. **Let it run for 10+ episodes** to verify stability

Then we can:
- Add real Claude Opus planning (Phase 2)
- Add real Veo 3.1 video generation (Phase 3)
- Deploy to production server

---

## Need Help?

Check these files:
- **QUICKSTART.md** - Fast reference
- **SETUP.md** - Detailed setup instructions
- **README.md** - Complete documentation
- **Plan file** - `~/.claude/plans/tender-swimming-kurzweil.md`

---

## Quick Test

```powershell
# 1. Setup (first time only)
.\setup.ps1

# 2. Run the system
python run_with_ui.py

# 3. Open browser
start http://localhost:8000

# 4. Watch episodes appear!
```

**Expected result:** You'll see Episode 1 appear in ~5 seconds, then Episode 2, 3, etc.

Press `Ctrl+C` when you're done testing.

---

## System Status

- ✅ **Phase 1:** Foundation (Complete)
- ✅ **Phase 4:** Web UI (Complete)
- ⏳ **Phase 2:** Director Integration (Next)
- ⏳ **Phase 3:** Real Video Generation (After Phase 2)
- ⏳ **Phase 5:** Production Hardening (Final)

**You're 40% done!** The core infrastructure is solid and ready to scale.

---

🎉 **Ready to generate infinite anime!**
