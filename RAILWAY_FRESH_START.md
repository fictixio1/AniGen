# Railway Fresh Start - Step by Step

## Step 1: Clean Slate

1. Go to https://railway.app/dashboard
2. Find your current AniGen project (the broken one)
3. Click on the project
4. Click the project name at top → "Project Settings"
5. Scroll to bottom → "Delete Project"
6. Type project name to confirm
7. Click "Delete"

---

## Step 2: Create New Project

1. Click "New Project"
2. Select "Empty Project"
3. Name it: `AniGen`
4. Click in project (should be empty)

---

## Step 3: Add PostgreSQL Database

1. Click "+ New" button
2. Select "Database"
3. Select "PostgreSQL"
4. Wait 10 seconds for it to provision
5. ✅ Done - PostgreSQL is now running with DATABASE_URL automatically set

---

## Step 4: Add Worker Service (Episode Generator)

1. Click "+ New" button again
2. Select "GitHub Repo"
3. Select `fictixio1/AniGen`
4. Wait for deployment to start

**Configure Worker Service:**

5. Click on the new service (should be building)
6. Click "Settings" tab
7. Find "Service Name" → rename to `worker`
8. Find "Start Command" → enter: `python start_worker.py`
9. Click "Deploy" (redeploys with new start command)

**Add Environment Variables:**

10. Click "Variables" tab
11. Click "+ New Variable" and add these ONE BY ONE:
    - `GENERATION_MODE` = `mock`
    - `SCENES_PER_EPISODE` = `6`
    - `SCENE_GENERATION_INTERVAL_MINUTES` = `10`
    - `LOG_LEVEL` = `INFO`

**Link Database:**

12. Still in Variables tab, look for "+ Reference" button
13. Click "+ Reference"
14. Select "Postgres" service
15. Select "DATABASE_URL" variable
16. Click "Add"

**Verify:**

17. Click "Deployments" tab → should see successful deployment
18. Click "Logs" tab → should see:
    ```
    Config loaded - DATABASE_URL from env: postgresql://...
    AniGen Orchestrator Starting...
    Starting Episode 1
    ```

---

## Step 5: Add API Service (Web Interface)

1. Click "+ New" button again
2. Select "GitHub Repo"
3. Select `fictixio1/AniGen` (same repo, different service)
4. Wait for deployment to start

**Configure API Service:**

5. Click on the new service
6. Click "Settings" tab
7. Find "Service Name" → rename to `api`
8. Find "Start Command" → enter: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
9. Scroll to "Networking" section
10. Click "Generate Domain"
11. **COPY THIS URL** (like `https://anigen-api-production.up.railway.app`)
12. Click "Deploy" (redeploys with new settings)

**Add Environment Variables:**

13. Click "Variables" tab
14. Add the same variables as worker service:
    - `GENERATION_MODE` = `mock`
    - `SCENES_PER_EPISODE` = `6`
    - `SCENE_GENERATION_INTERVAL_MINUTES` = `10`
    - `LOG_LEVEL` = `INFO`

**Link Database:**

15. Click "+ Reference"
16. Select "Postgres" service
17. Select "DATABASE_URL" variable
18. Click "Add"

**Verify:**

19. Click "Deployments" tab → should see successful deployment
20. Visit the domain URL (from step 11) in browser
21. You should see API docs or JSON response

---

## Step 6: Test the System

### Test API Endpoint:
Visit: `https://your-api-url.railway.app/api/episodes`

Should return JSON like:
```json
[]
```
(empty at first, then episodes will appear as worker generates them)

### Check Worker Logs:
1. Click on "worker" service
2. Click "Logs" tab
3. Should see:
   ```
   Starting Episode 1
   Scene 1/6
   Scene 2/6
   ...
   Episode 1 Complete!
   ```

### Check Database:
1. Click on "Postgres" service
2. Click "Data" tab (if available)
3. Or click "Connect" to get connection string

---

## Troubleshooting

### Worker keeps crashing with "DATABASE_URL not set"
- Go to worker service → Variables
- Make sure you see `DATABASE_URL` with a value (from Reference)
- If not, add the reference again (Step 4, item 12-16)

### API returns 500 error
- Same issue - check API service → Variables
- Make sure DATABASE_URL is there

### No episodes being generated
- Check worker service logs
- Make sure it says "Starting Episode 1"
- If you see errors, paste them here

### Services won't start
- Check if they're using correct start commands:
  - Worker: `python start_worker.py`
  - API: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`

---

## Final Architecture

You should now have:

```
Railway Project: AniGen
├── Postgres (database)
│   └── DATABASE_URL automatically set
├── worker (episode generator)
│   ├── Reads DATABASE_URL from Postgres reference
│   └── Generates episodes every 60 min
└── api (web API)
    ├── Reads DATABASE_URL from Postgres reference
    └── Serves episodes at public URL
```

---

## What to Give Me After Setup

Once you're done, tell me:

1. ✅ Worker service status (running/crashed)
2. ✅ API service public URL
3. ✅ Any errors in logs

Then we'll deploy the Vercel frontend!
