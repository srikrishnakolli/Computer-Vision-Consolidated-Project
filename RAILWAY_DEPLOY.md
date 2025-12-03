# Railway Deployment Guide

This guide explains how to deploy the Computer Vision Assignments web application to Railway.

## Prerequisites

1. A Railway account (sign up at [railway.app](https://railway.app))
2. Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Prepare Your Repository

The application is already configured for Railway with:
- `app.py` - Main Flask server
- `requirements.txt` - Python dependencies
- `Procfile` - Railway process configuration
- `runtime.txt` - Python version specification

### 2. Connect to Railway

1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo" (or your Git provider)
4. Select your repository
5. Railway will automatically detect the Python project

### 3. Configure Environment Variables

Railway will automatically:
- Set the `PORT` environment variable
- Install dependencies from `requirements.txt`
- Run the application using the `Procfile`

No additional configuration is needed!

### 4. Deploy

Railway will automatically:
1. Build your application
2. Install dependencies
3. Start the server using Gunicorn
4. Assign a public URL

### 5. Access Your Application

Once deployed, Railway will provide:
- A public URL (e.g., `https://your-app.railway.app`)
- All assignments accessible at the root URL
- API endpoints at `/api/*`

## File Structure for Railway

```
.
├── app.py                 # Main Flask server
├── requirements.txt       # Python dependencies
├── Procfile              # Railway process file
├── runtime.txt           # Python version
├── index.html            # Main hub page
├── assignments/          # All assignment files
│   ├── assignment1/
│   ├── assignment2/
│   ├── assignment3/
│   ├── assignment4/
│   ├── assignment5-6/
│   └── assignment7/
└── .railwayignore        # Files to exclude from deployment
```

## Important Notes

### Static File Serving
- The Flask server serves all static files (HTML, CSS, JS, images)
- Files are served from the root and `assignments/` folders
- Paths are automatically resolved

### API Endpoints
- All API endpoints are at `/api/*`
- Frontend automatically uses `window.location.origin + '/api'`
- Works in both local and production environments

### Backend Services
- Assignment 7 backend API is integrated into the main server
- No separate backend service needed
- All endpoints are available at `/api/*`

### OpenCV.js
- Assignment 3 uses local OpenCV.js build (included in deployment)
- Other assignments use CDN-hosted OpenCV.js
- All dependencies are handled automatically

## Troubleshooting

### Build Fails
- Check that `requirements.txt` is correct
- Verify Python version in `runtime.txt` is supported
- Check Railway build logs for specific errors

### Static Files Not Loading
- Verify file paths in HTML files
- Check that files exist in the repository
- Review `.railwayignore` to ensure files aren't excluded

### API Not Working
- Verify API endpoints are at `/api/*`
- Check browser console for CORS errors
- Ensure Flask-CORS is installed and configured

### Port Issues
- Railway automatically sets the `PORT` environment variable
- The app uses `PORT` from environment (defaults to 5000)
- No manual port configuration needed

## Custom Domain

To use a custom domain:
1. Go to your Railway project settings
2. Click "Domains"
3. Add your custom domain
4. Follow Railway's DNS configuration instructions

## Monitoring

Railway provides:
- Real-time logs
- Metrics dashboard
- Error tracking
- Automatic restarts on crashes

## Updates

To update your deployment:
1. Push changes to your Git repository
2. Railway automatically detects changes
3. Rebuilds and redeploys automatically
4. Zero-downtime deployments

## Cost Considerations

- Railway offers a free tier with usage limits
- Check Railway pricing for production usage
- Consider upgrading for higher traffic

## Support

For issues:
1. Check Railway logs in the dashboard
2. Review application logs in `app.py`
3. Check browser console for frontend errors
4. Verify all dependencies are installed

