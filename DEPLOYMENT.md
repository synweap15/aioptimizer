# Deployment Guide

## Cloudflare Pages Setup for Frontend

### Initial Setup (Already Completed)

The Cloudflare Pages project has been created and configured:

1. **Project Created**: `aioptimizer`
2. **Production URL**: https://aioptimizer.pages.dev/
3. **Account ID**: `d371c76d7e486fbae757ae73a6349bc6`
4. **Account**: Shamdog+cloudflare@gmail.com's Account

### Connect to GitHub (Manual Steps Required)

To enable automatic deployments from GitHub:

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Navigate to **Workers & Pages** > **aioptimizer**
3. Go to **Settings** > **Builds & deployments**
4. Click **Connect to Git**
5. Select GitHub and authorize Cloudflare
6. Choose repository: `synweap15/aioptimizer`
7. Configure build settings:
   - **Production branch**: `master`
   - **Build command**: `npm run build`
   - **Build output directory**: `.next`
   - **Root directory**: `frontend`
   - **Environment variables** (optional):
     - `NEXT_PUBLIC_API_URL`: Your production API URL

### How It Works

Once connected to GitHub:

- **Automatic Deployments**: Every push to `master` branch triggers a new deployment
- **Preview Deployments**: Pull requests get their own preview URLs
- **Build Logs**: View build progress and logs in Cloudflare Dashboard
- **Rollback**: Easy rollback to previous deployments from the dashboard

### Manual Deployment via CLI

If you prefer to deploy manually using Wrangler:

```bash
# Ensure you're using Node.js v24
nvm use v24

# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build the application
npm run build

# Deploy to Cloudflare Pages
CLOUDFLARE_ACCOUNT_ID=d371c76d7e486fbae757ae73a6349bc6 wrangler pages deploy .next --project-name=aioptimizer
```

### Environment Variables

Set environment variables in Cloudflare Dashboard:

1. Go to **Workers & Pages** > **aioptimizer** > **Settings** > **Environment variables**
2. Add variables for production:
   - `NEXT_PUBLIC_API_URL`: Production backend API URL
3. Add variables for preview (optional)

### Build Configuration

The `wrangler.toml` file contains:

```toml
name = "aioptimizer"
compatibility_date = "2024-01-01"
pages_build_output_dir = ".next"
account_id = "d371c76d7e486fbae757ae73a6349bc6"

[build]
command = "npm run build"
```

### Troubleshooting

#### Build Failures

Check the build logs in Cloudflare Dashboard:
1. Go to **Workers & Pages** > **aioptimizer** > **View build**
2. Review the error messages

Common issues:
- **Missing environment variables**: Add them in Settings
- **Node.js version**: Cloudflare uses Node 18 by default; add `NODE_VERSION=24` env var if needed
- **Build timeout**: Increase timeout in settings or optimize build

#### Deployment Not Triggering

1. Verify GitHub integration is active
2. Check that you pushed to the `master` branch
3. Ensure the repository webhook is configured in GitHub settings

### Custom Domains

To add a custom domain:

1. Go to **Workers & Pages** > **aioptimizer** > **Custom domains**
2. Click **Set up a custom domain**
3. Follow the DNS configuration instructions

### Monitoring

Monitor your deployments:

- **Analytics**: Workers & Pages > aioptimizer > Analytics
- **Real-time logs**: Available in dashboard
- **Alerts**: Configure email alerts for build failures

---

## Backend Deployment Options

### Option 1: Docker Compose (Recommended for VPS)

Deploy on a VPS with Docker:

```bash
# Clone repository
git clone https://github.com/synweap15/aioptimizer.git
cd aioptimizer

# Create .env file
cp backend/.env.example backend/.env
# Edit backend/.env with production values

# Start services
docker-compose -f docker-compose.production.yml up -d

# Run migrations
docker exec aioptimizer-backend poetry run alembic upgrade head
```

### Option 2: Manual Deployment

Deploy on a VPS without Docker:

```bash
# Install dependencies
cd backend
poetry install --no-dev

# Run migrations
poetry run alembic upgrade head

# Start with Uvicorn
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Option 3: Railway/Render/Fly.io

These platforms support FastAPI deployments:

1. Connect your GitHub repository
2. Set build command: `cd backend && poetry install`
3. Set start command: `cd backend && poetry run uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `backend/.env.example`
5. Deploy

---

## CI/CD Pipeline

### Current Setup

- **Frontend**: Cloudflare Pages auto-deploys from GitHub
- **Backend**: Manual deployment (can be automated)

### Future Enhancements

1. **Backend CI/CD**: Add GitHub Actions for backend deployment
2. **Testing**: Run tests before deployment
3. **Database Migrations**: Auto-run migrations on deploy
4. **Health Checks**: Verify deployment success

---

## Production Checklist

Before going to production:

### Backend

- [ ] Set strong `SECRET_KEY` in environment variables
- [ ] Configure production database (not localhost)
- [ ] Set `RELEASE_STAGE=production`
- [ ] Enable HTTPS
- [ ] Configure CORS for production frontend URL
- [ ] Set up database backups
- [ ] Configure Redis for production
- [ ] Add monitoring (Sentry, LogRocket, etc.)
- [ ] Set up SSL certificates

### Frontend

- [ ] Set `NEXT_PUBLIC_API_URL` to production backend
- [ ] Test build locally: `npm run build && npm start`
- [ ] Configure custom domain (optional)
- [ ] Enable caching headers
- [ ] Set up error tracking
- [ ] Configure analytics

### Security

- [ ] Review and update CORS settings
- [ ] Enable rate limiting
- [ ] Set up WAF rules (Cloudflare)
- [ ] Configure security headers
- [ ] Enable HTTPS only
- [ ] Regular security updates

---

## Rollback Procedures

### Frontend (Cloudflare Pages)

1. Go to **Workers & Pages** > **aioptimizer** > **Deployments**
2. Find the previous working deployment
3. Click **Rollback to this deployment**

### Backend

1. SSH into your server
2. Pull previous version: `git checkout <previous-commit>`
3. Restart service: `docker-compose restart backend`
4. Or rollback database: `poetry run alembic downgrade -1`

---

## Monitoring & Logs

### Frontend (Cloudflare)

- **Build logs**: Cloudflare Dashboard > Workers & Pages > View build
- **Real-time logs**: Available in Cloudflare Dash
- **Analytics**: Cloudflare Analytics tab

### Backend

- **Application logs**: `docker-compose logs -f backend`
- **Access logs**: Uvicorn outputs to stdout
- **Error tracking**: Integrate Sentry or similar

---

## Cost Estimate

### Cloudflare Pages (Frontend)

- **Free tier**: 500 builds/month, unlimited requests
- **Pro plan**: $20/month (if exceeding free tier)

### Backend (VPS)

- **Small VPS**: $5-10/month (DigitalOcean, Linode)
- **Medium VPS**: $20-40/month (for production traffic)

### Database

- **Managed MySQL**: $15-50/month (depends on provider)
- **Self-hosted**: Included in VPS cost

### Total Estimate

- **Development**: Free (Cloudflare Pages free tier + local backend)
- **Production**: $20-100/month (depending on traffic and requirements)
