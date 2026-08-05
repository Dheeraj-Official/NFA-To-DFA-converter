# Deployment Guide - Render.com

This guide will help you deploy your NFA to DFA converter web application to Render.com for free.

## 📋 Prerequisites

Before deploying, ensure you have:

- [x] A GitHub account with your project pushed to a repository
- [x] A Render.com account (free)
- [x] All project files committed to git
- [x] `.gitignore` updated to include the C++ executable

## 🚀 Deployment Steps

### 1. Prepare Your Git Repository

First, ensure your project is properly committed to git:

```bash
# Navigate to your project directory
cd C:\Users\dheer\Downloads\01

# Initialize git if not already done
git init

# Add all files
git add .

# Commit changes
git commit -m "Prepare for Render.com deployment"

# Add remote repository (replace with your GitHub repo)
git remote add origin https://github.com/your-username/your-repo.git

# Push to GitHub
git push -u origin main
```

### 2. Sign Up for Render.com

1. Go to [render.com](https://render.com)
2. Click "Sign Up"
3. Sign up with GitHub (recommended)
4. Render will ask for access to your GitHub repositories

### 3. Deploy Backend (API Service)

#### Option A: Using render.yaml (Recommended)

If you've committed the `render.yaml` file, Render will automatically detect it:

1. In Render dashboard, click "New +"
2. Select "Existing repository"
3. Choose your repository
4. Render will detect the `render.yaml` configuration
5. Click "Apply" to deploy both services

#### Option B: Manual Deployment

If you prefer manual setup:

1. In Render dashboard, click "New +"
2. Select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `nfa-dfa-api`
   - **Environment**: Docker
   - **Dockerfile Path**: `./backend/Dockerfile`
   - **Docker Context**: `./backend`
   - **Plan**: Free
5. Add Environment Variables:
   - `PORT`: `5000`
   - `ALLOWED_ORIGINS`: `https://nfa-dfa-frontend.onrender.com` (or use `*` for testing)
6. Click "Create Web Service"

### 4. Deploy Frontend (Static Site)

#### Option A: Using render.yaml (Recommended)

If using `render.yaml`, the frontend will be deployed automatically with the backend.

#### Option B: Manual Deployment

1. In Render dashboard, click "New +"
2. Select "Static Site"
3. Connect your GitHub repository
4. Configure the site:
   - **Name**: `nfa-dfa-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
   - **Plan**: Free
5. Add Environment Variable (if needed):
   - `VITE_API_URL`: `https://nfa-dfa-api.onrender.com/api/convert`
6. Click "Create Static Site"

### 5. Update API URLs After Deployment

After both services are deployed:

1. **Backend URL**: Check your Render dashboard for the backend URL (e.g., `https://nfa-dfa-api.onrender.com`)
2. **Frontend URL**: Check your Render dashboard for the frontend URL (e.g., `https://nfa-dfa-frontend.onrender.com`)

#### Update Backend CORS Settings:

1. Go to your backend service in Render dashboard
2. Scroll to "Environment Variables"
3. Update `ALLOWED_ORIGINS` to your actual frontend URL:
   ```
   https://nfa-dfa-frontend.onrender.com
   ```
4. Save changes (this will trigger a redeploy)

#### Update Frontend API URL:

Since Render static sites don't support build-time environment variables well, you have two options:

**Option 1: Hardcode the URL (Simplest)**

Update `frontend/src/App.jsx`:
```javascript
// Replace this line:
const API_URL = import.meta.env.VITE_API_URL || '/api/convert'

// With this:
const API_URL = 'https://nfa-dfa-api.onrender.com/api/convert'
```

**Option 2: Use Runtime Detection**

Update `frontend/src/App.jsx`:
```javascript
const API_URL = window.location.hostname === 'localhost' 
  ? '/api/convert' 
  : 'https://nfa-dfa-api.onrender.com/api/convert'
```

### 6. Test Your Deployment

1. Open your frontend URL in a browser
2. Test the "Load Example" button
3. Click "Convert to DFA"
4. Verify that all three diagrams (NFA, DFA, Minimized DFA) appear correctly
5. Test zoom, pan, and fullscreen features

## 🔧 Troubleshooting

### Backend Not Starting

**Issue**: Backend fails to start or shows compilation errors

**Solutions**:
- Check Render logs in the dashboard
- Ensure the C++ source file (`01_NFA_To_DFA.cpp`) is committed
- Verify Graphviz is installed (it should be in the Docker image)
- Check that the Dockerfile path is correct in render.yaml

### CORS Errors

**Issue**: Frontend shows CORS errors when calling the API

**Solutions**:
- Update `ALLOWED_ORIGINS` in backend environment variables
- Ensure the frontend URL is correct (no trailing slashes)
- Use `*` for testing (not recommended for production)
- Check that the backend CORS middleware is properly configured

### API Timeouts

**Issue**: First API call takes a long time (~30 seconds)

**Solution**: This is normal for the free tier. The backend "sleeps" after 15 minutes of inactivity and needs time to wake up. Subsequent calls will be faster.

### Build Failures

**Issue**: Frontend build fails

**Solutions**:
- Check that `package.json` is in the `frontend/` directory
- Ensure all dependencies are in `package.json`
- Verify the build command: `cd frontend && npm install && npm run build`
- Check Render build logs for specific errors

### 404 Errors

**Issue**: API calls return 404 errors

**Solutions**:
- Verify the API URL is correct
- Check that the backend is running (check Render dashboard)
- Ensure the endpoint path is `/api/convert`
- Check backend logs for any errors

## 🔄 CI/CD with Render

Render automatically deploys when you push to your connected branch (usually `main`):

```bash
# Make changes locally
git add .
git commit -m "Your changes"
git push origin main

# Render will automatically detect the push and redeploy
```

## 💰 Cost Information

### Free Tier Limits:

- **Backend (Web Service)**: 750 hours/month (enough for always-on)
- **Frontend (Static Site)**: Unlimited bandwidth and storage
- **Total Cost**: $0/month

### When to Upgrade:

Consider upgrading to paid tier if:
- You need faster cold starts (backend always-on)
- You expect high traffic
- You need custom domains
- You need additional features

Paid tier starts at $7/month for the backend.

## 🌐 Custom Domain (Optional)

If you want to use a custom domain:

1. Purchase a domain from a registrar
2. In Render dashboard, go to your service settings
3. Add your custom domain
4. Update DNS records as instructed by Render
5. Update CORS settings with your new domain

## 📊 Monitoring

Render provides built-in monitoring:

- **Logs**: View real-time logs in the dashboard
- **Metrics**: CPU, memory, and response time metrics
- **Deployments**: View deployment history and logs
- **Health Checks**: Automatic health monitoring

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` files
2. **CORS**: Use specific origins instead of `*` in production
3. **API Keys**: If you add API keys later, store them in environment variables
4. **HTTPS**: Render automatically provides SSL certificates
5. **Dependencies**: Keep dependencies updated for security

## 🚀 Alternative Deployment Platforms

If Render doesn't work for you, consider:

- **Railway.app**: Similar to Render, good Docker support
- **Fly.io**: More advanced, global deployment
- **Vercel + PythonAnywhere**: Separate frontend/backend hosting
- **Heroku**: Paid option, but very reliable

## 📝 Post-Deployment Checklist

- [ ] Backend deployed and accessible
- [ ] Frontend deployed and accessible
- [ ] CORS configured correctly
- [ ] API URL updated in frontend
- [ ] Example loading works
- [ ] NFA to DFA conversion works
- [ ] DFA minimization works
- [ ] Diagrams display correctly
- [ ] Interactive features (zoom, pan, fullscreen) work
- [ ] Logs are clean (no errors)
- [ ] HTTPS is working
- [ ] Mobile responsiveness is maintained

## 🆘 Getting Help

If you encounter issues:

1. Check Render [documentation](https://render.com/docs)
2. Review Render logs in the dashboard
3. Check this deployment guide
4. Verify your `render.yaml` configuration
5. Ensure all files are committed to git

## 🎉 Success!

Your NFA to DFA converter is now live on Render.com! Share your URL with others and enjoy your free hosting.

**Your URLs will be:**
- Frontend: `https://nfa-dfa-frontend.onrender.com`
- Backend: `https://nfa-dfa-api.onrender.com`
