# Railway Deployment Troubleshooting

## Problem: Railway trying to use mise/Nixpacks instead of Docker

### Solution 1: Configure Railway Dashboard (RECOMMENDED)

1. Go to your Railway project dashboard
2. Click on your service
3. Go to **Settings** → **Deploy**
4. Look for **"Builder"** or **"Build Command"** option
5. Change from **"Nixpacks"** to **"Dockerfile"**
6. Click **Save**
7. Click **"Redeploy"** or push a new commit

### Solution 2: Force Docker via Railway CLI

If you have Railway CLI installed:

```bash
railway variables set NIXPACKS_BUILDER=false
railway redeploy
```

### Solution 3: Create New Service

1. In Railway dashboard, create a **NEW** service
2. Select **"GitHub Repo"**
3. Choose your repository
4. Railway should auto-detect the `Dockerfile` and `railway.toml`
5. Delete the old service if needed

### Solution 4: Verify Files are Correct

Make sure these files exist in your repository:

- ✅ `Dockerfile` (present)
- ✅ `railway.toml` (present)
- ✅ `requirements.txt` (present)
- ✅ `app.py` (present)
- ✅ `Procfile` (present)
- ❌ `runtime.txt` (removed - conflicts with Docker)
- ❌ `nixpacks.toml` (should not exist)
- ❌ Any `mise.toml` or `.tool-versions` files (should not exist)

### Solution 5: Manual Docker Build Test

Test locally to ensure Dockerfile works:

```bash
docker build -t computer-vision-app .
docker run -p 5000:5000 -e PORT=5000 computer-vision-app
```

If this works locally, Railway should work too.

### Current Configuration

Your project now has:

1. **`Dockerfile`** - Uses `python:3.11-slim` directly (no mise)
2. **`railway.toml`** - Explicitly tells Railway to use Dockerfile
3. **`.dockerignore`** - Excludes unnecessary files
4. **No `runtime.txt`** - Removed to prevent Nixpacks detection

### After Making Changes

1. Push changes to GitHub
2. Go to Railway dashboard
3. Verify it's using Docker (check build logs)
4. If still using mise, manually change builder in Railway settings

