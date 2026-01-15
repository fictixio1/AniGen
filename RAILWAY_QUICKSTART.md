# Railway Quick Start - Deploy in 5 Minutes

This is the **fastest way** to get AniGen running in the cloud.

## Prerequisites

1. **Node.js installed** (for Railway CLI)
   - Download: https://nodejs.org
   - Check: `node --version`

2. **Railway account** (free tier available)
   - Sign up: https://railway.app
   - Uses GitHub login

## Option 1: Automated Deployment (Windows)

**Just run this:**
```powershell
.\DEPLOY_NOW.bat
```

The script will:
- Install Railway CLI
- Login to Railway
- Create new project
- Add PostgreSQL database
- Set environment variables
- Deploy the system

## Option 2: Manual Deployment (All Platforms)

### Step 1: Install Railway CLI

**Windows (PowerShell):**
```powershell
npm i -g @railway/cli
```

**Mac/Linux:**
```bash
npm i -g @railway/cli
```

### Step 2: Login

```bash
railway login
```

This opens your browser to authenticate with GitHub.

### Step 3: Initialize Project

```bash
cd C:\Users\klent\OneDrive\Documents\CODE\AniGen
railway init
```

When prompted:
- Select: **"Create new project"**
- Name it: **"anigen"** (or whatever you want)

### Step 4: Add Database

```bash
railway add --database postgres
```

Railway automatically:
- Creates PostgreSQL database
- Sets `DATABASE_URL` environment variable
- Initializes tables on first run

### Step 5: Configure Environment

```bash
railway variables set GENERATION_MODE=mock
railway variables set SCENES_PER_EPISODE=6
railway variables set SCENE_GENERATION_INTERVAL_MINUTES=10
railway variables set LOG_LEVEL=INFO
```

For production with real API keys:
```bash
railway variables set GENERATION_MODE=real
railway variables set ANTHROPIC_API_KEY=your_key_here
railway variables set GOOGLE_AI_API_KEY=your_key_here
```

### Step 6: Deploy

```bash
railway up
```

This uploads your code and starts the system!

### Step 7: View Logs

```bash
railway logs --follow
```

You'll see episodes being generated in real-time.

### Step 8: Open Dashboard

```bash
railway open
```

Opens Railway dashboard where you can:
- See database
- View logs
- Check metrics
- Get public URL for web UI

## What Gets Deployed

Railway will create **2 services**:

### 1. Worker Service (Background)
- Runs `start_worker.py`
- Generates episodes continuously
- One episode every 60 minutes (6 scenes)
- One scene every 10 minutes

### 2. Web Service (Public URL)
- Runs FastAPI application
- Accessible at `https://your-app.railway.app`
- Shows episode list and playback
- Auto-refreshes every 10 minutes

## Viewing the Web UI

After deployment:

1. Get your public URL:
   ```bash
   railway open
   ```

2. Look for the **"web"** service

3. Click the **"Open"** button or copy the URL

4. Visit in browser: `https://anigen-production.up.railway.app`

You'll see:
- List of generated episodes
- Episode details (6 scenes each)
- Video playback
- Series statistics

## Monitoring

### View Logs
```bash
# All logs
railway logs

# Follow live
railway logs --follow

# Specific service
railway logs --service worker
railway logs --service web
```

### Check Database
```bash
# Connect to PostgreSQL
railway connect postgres

# Or get connection string
railway variables get DATABASE_URL
```

Then use any PostgreSQL client (pgAdmin, DBeaver, etc.)

### View Metrics
```bash
railway status
```

Shows:
- Service health
- CPU/memory usage
- Build status
- Deployment history

## Updating the System

To deploy changes:

```bash
git add .
git commit -m "Update system"
railway up
```

Or if using GitHub integration, just push:
```bash
git push
```

Railway auto-deploys on push!

## Stopping the System

### Pause generation (keeps database)
In Railway dashboard:
1. Go to worker service
2. Click "Stop"

### Delete everything
```bash
railway down
```

**Warning:** This deletes the database too!

## Costs

### Free Tier
- $5 credit per month
- 500 hours runtime
- Perfect for testing

### Hobby Plan ($5/month)
- $5 subscription + usage
- Unlimited projects
- Recommended for continuous generation

### Estimated Monthly Cost
- PostgreSQL database: $5-10
- Worker service: $5-10
- Web service: $5
- **Total: ~$15-25/month**

Plus API costs:
- Mock mode: $0 (no real generation)
- Production mode: ~$20k/month (Veo 3.1 Fast + Claude Opus)

## Troubleshooting

### "railway: command not found"
Install Node.js first: https://nodejs.org

### "Database connection failed"
Railway sets `DATABASE_URL` automatically. Make sure `config.py` reads it from environment.

### "Service won't start"
Check logs:
```bash
railway logs --service worker
```

Common issues:
- Missing environment variables
- Database not initialized
- Wrong Python version (needs 3.11+)

### "Out of free credits"
Upgrade to Hobby plan ($5/month):
1. Go to https://railway.app/account
2. Click "Upgrade"
3. Choose Hobby plan

## Production Checklist

Before going to production:

- [ ] Set `GENERATION_MODE=real`
- [ ] Add API keys (Anthropic, Google)
- [ ] Set up AWS S3 for video storage
- [ ] Configure cost limits
- [ ] Set up monitoring/alerts
- [ ] Enable database backups
- [ ] Add custom domain (optional)

## Next Steps

Once deployed:

1. ✅ Check logs: `railway logs --follow`
2. ✅ Watch episodes generate
3. ✅ Access web UI at your Railway URL
4. ✅ Query database to see stored episodes
5. ✅ Move to Phase 2 (real Claude Opus integration)

## Need Help?

- Railway docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- This project's issues: https://github.com/yourusername/anigen/issues

## Alternative: Deploy via GitHub

Don't want to use CLI? Deploy via GitHub instead:

1. Create new GitHub repository
2. Push this code to GitHub
3. Go to https://railway.app/new
4. Click "Deploy from GitHub repo"
5. Select your repository
6. Railway auto-detects Python and deploys!

See [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md) for detailed GitHub deployment instructions.
