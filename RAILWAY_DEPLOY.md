# Deploy AniGen to Railway

## Step-by-Step Deployment

### 1. Create Railway Account
1. Go to https://railway.app
2. Click "Sign up with GitHub"
3. Authorize Railway

### 2. Install Railway CLI
```powershell
# Install via npm
npm i -g @railway/cli

# OR download from https://docs.railway.app/develop/cli#install
```

### 3. Initialize Git Repository (if not already done)
```powershell
cd C:\Users\klent\OneDrive\Documents\CODE\AniGen

git init
git add .
git commit -m "Initial commit"
```

### 4. Login to Railway
```powershell
railway login
```

This will open your browser to authenticate.

### 5. Create New Project
```powershell
railway init
```

Select "Create new project" and give it a name like "anigen"

### 6. Add PostgreSQL Database
```powershell
railway add --database postgres
```

Railway will automatically:
- Create a PostgreSQL database
- Set the `DATABASE_URL` environment variable
- Initialize the database

### 7. Set Environment Variables
```powershell
# Set generation mode
railway variables set GENERATION_MODE=mock

# Set scene configuration
railway variables set SCENES_PER_EPISODE=6
railway variables set SCENE_GENERATION_INTERVAL_MINUTES=10

# Set API keys (when ready for production)
# railway variables set ANTHROPIC_API_KEY=your_key_here
# railway variables set GOOGLE_AI_API_KEY=your_key_here
# railway variables set OPENAI_API_KEY=your_key_here
```

### 8. Deploy!
```powershell
railway up
```

This will:
- Upload your code
- Install dependencies
- Connect to PostgreSQL
- Start the orchestrator
- Begin generating episodes!

### 9. View Logs
```powershell
railway logs
```

You'll see episodes being generated in real-time!

### 10. Open Dashboard
```powershell
railway open
```

This opens the Railway dashboard where you can:
- See your database
- View logs
- Check metrics
- Manage environment variables

## Alternative: Deploy via GitHub

### 1. Push to GitHub
```powershell
# Create new repository on GitHub first, then:
git remote add origin https://github.com/yourusername/anigen.git
git branch -M main
git push -u origin main
```

### 2. In Railway Dashboard
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your `anigen` repository
4. Click "Add variables" and add:
   - `GENERATION_MODE=mock`
   - `SCENES_PER_EPISODE=6`
   - etc.
5. Click "Deploy"

Railway will automatically detect it's a Python app and deploy it!

## Add Web UI Service

To deploy the web UI alongside the orchestrator:

### 1. Create a second service
In Railway dashboard:
1. Click "New" → "Empty Service"
2. Connect to the same GitHub repo
3. Set start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
4. Railway will give you a public URL

### 2. Or use the CLI
```powershell
railway service create web
railway service set-start-command "uvicorn api.main:app --host 0.0.0.0 --port \$PORT"
railway up
```

Now you'll have:
- **Worker service**: Generates episodes (background)
- **Web service**: Public URL to view episodes

## Database Access

To query the database directly:

```powershell
# Connect to database
railway connect postgres

# Or get the connection string
railway variables get DATABASE_URL
```

Then use any PostgreSQL client to connect.

## Costs

Railway free tier includes:
- ✅ $5 of usage per month (enough for testing)
- ✅ 500 hours of runtime
- ✅ Unlimited projects
- ✅ PostgreSQL database

For production (24/7 running):
- **Hobby plan**: $5/month + usage
- **Pro plan**: $20/month + usage

Estimated monthly cost for AniGen:
- Database: $5-10/month
- Worker service: $5-10/month
- Web service: $5/month
- **Total: ~$15-25/month**

Plus API costs (~$20k/month for video generation in production mode)

## Monitoring

View real-time logs:
```powershell
railway logs --follow
```

View specific service:
```powershell
railway logs --service worker
railway logs --service web
```

## Updating

To deploy changes:
```powershell
git add .
git commit -m "Update system"
git push

# Railway auto-deploys on push!
# Or manually:
railway up
```

## Troubleshooting

### "Command not found: railway"
Install the CLI:
```powershell
npm i -g @railway/cli
```

### "Database connection failed"
Railway sets `DATABASE_URL` automatically. Make sure your code reads it:
```python
from config import config  # Reads DATABASE_URL from environment
```

### "Service won't start"
Check logs:
```powershell
railway logs
```

Common issues:
- Missing dependencies in `requirements.txt`
- Wrong start command
- Database not initialized

### "Out of credits"
Upgrade to Hobby plan ($5/month) for unlimited usage.

## Production Checklist

Before going to production:

- [ ] Set `GENERATION_MODE=real`
- [ ] Add all API keys (Anthropic, Google, OpenAI)
- [ ] Set up AWS S3 for video storage
- [ ] Configure cost limits
- [ ] Set up monitoring/alerts
- [ ] Enable database backups
- [ ] Add custom domain (optional)

## Next Steps

Once deployed:

1. Check logs: `railway logs`
2. Watch episodes generate
3. Access web UI at your Railway URL
4. Query database to see stored episodes
5. Move to Phase 2 (real Claude Opus integration)

Railway handles:
- ✅ Automatic deployments
- ✅ Database backups
- ✅ SSL certificates
- ✅ Scaling
- ✅ Monitoring

You just write code and push!
