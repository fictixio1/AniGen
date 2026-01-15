# AniGen Quick Start 🚀

## One-Command Setup

### Windows (PowerShell)
```powershell
.\setup.ps1
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

## Manual Setup (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Database
```bash
# Option A: Docker (recommended)
docker compose up -d postgres

# Option B: Local PostgreSQL
psql -U postgres -c "CREATE DATABASE anigen;"
psql -U postgres -c "CREATE USER anigen_user WITH PASSWORD 'anigen_password';"
psql -U anigen_user -d anigen -f schemas/database_schema.sql
```

### 3. Run System
```bash
python main.py
```

## What You'll See

```
============================================================
Starting Episode 1
============================================================
Director planning episode 1

Generating Scene 1/6 (Global #1)
✓ Scene 1 completed: mock://video/1736938801.mp4

Generating Scene 2/6 (Global #2)
✓ Scene 2 completed: mock://video/1736938811.mp4

...

============================================================
Episode 1 Complete!
Total Cost: $27.66
Duration: 180s
============================================================
```

## Check Database

```sql
-- Connect
psql -U anigen_user -d anigen

-- View episodes
SELECT episode_number, episode_arc_summary, total_cost_usd
FROM episodes
ORDER BY episode_number DESC;

-- View scenes
SELECT scene_number, scene_in_episode, narrative_summary
FROM scenes
ORDER BY scene_number DESC
LIMIT 10;

-- Check system state
SELECT * FROM series_state;
```

## Common Commands

| Action | Command |
|--------|---------|
| Start system | `python main.py` |
| Stop system | Press `Ctrl+C` |
| Check DB | `psql -U anigen_user -d anigen` |
| View logs | Check database `generation_logs` table |
| Restart DB (Docker) | `docker compose restart postgres` |

## Troubleshooting

### "Database connection failed"
```bash
# Check if PostgreSQL is running
docker ps | grep postgres
# OR
pg_ctl status

# Restart if needed
docker compose restart postgres
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Port 5432 already in use"
```bash
# Change port in docker-compose.yml
ports:
  - "5433:5432"

# Update .env
DATABASE_URL=postgresql://anigen_user:anigen_password@localhost:5433/anigen
```

## System Stats

**Mock Mode (Current):**
- Episodes/hour: 720 (testing speed)
- Cost: $0 (simulated)
- Database: ~1MB per 100 episodes

**Production Mode (Future):**
- Episodes/hour: 1 (real generation)
- Cost: ~$27.66 per episode
- Total: ~$664/day, ~$19,915/month

## Next Phase

Once mock mode is working, we can:
1. **Add Web UI** - View episodes in browser
2. **Integrate Claude Opus** - Real episode planning
3. **Add Veo 3.1** - Real video generation
4. **Deploy** - Run 24/7 in production

## File Structure

```
AniGen/
├── main.py              ← Start here
├── config.py            ← Configuration
├── database.py          ← DB connection
├── canon.py             ← Canon memory
├── episode_manager.py   ← Episode lifecycle
├── .env                 ← Your settings
├── docker-compose.yml   ← Database config
└── schemas/
    └── database_schema.sql  ← Database structure
```

## Need Help?

- Full docs: [README.md](README.md)
- Setup guide: [SETUP.md](SETUP.md)
- Architecture: `~/.claude/plans/tender-swimming-kurzweil.md`
