# Docker Deployment Guide

## Overview

This guide explains how to deploy the entire chat application using Docker and Docker Compose.

## Files

- **Dockerfile**: Multi-stage build for production
  - Stage 1: Builds React frontend with Node.js
  - Stage 2: Packages backend with Python and includes built frontend
  - Result: Single optimized image containing frontend + backend

- **docker-compose.yml**: Orchestrates all services
  - PostgreSQL database
  - Redis cache
  - FastAPI app (frontend + backend)

- **.dockerignore**: Excludes unnecessary files from Docker build

- **.env.example**: Template for environment variables

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 1.29+)

## Quick Start

### 1. Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set required variables:

```env
DB_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_change_in_production
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Build and Start Services

```bash
docker-compose up -d
```

This will:
- Build the Docker image (first run takes 3-5 minutes)
- Start PostgreSQL, Redis, and the app
- Initialize the database

### 3. Verify Services

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs -f app

# Test health endpoint
curl http://localhost:8000/health
```

### 4. Access the Application

- Frontend: http://localhost:8000
- API: http://localhost:8000/api/v1

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f          # All services
docker-compose logs -f app      # Just the app
docker-compose logs -f postgres # Just the database
```

### Rebuild after code changes
```bash
docker-compose up -d --build
```

### Execute commands in container
```bash
# Run Python command
docker-compose exec app python -c "import app; print('ok')"

# Access database
docker-compose exec postgres psql -U postgres -d chatapp
```

### Remove everything (including data)
```bash
docker-compose down -v
```

## Production Deployment

### Important Security Changes

Before deploying to production:

1. **Change the SECRET_KEY** in `.env`
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Use a strong database password**
   ```bash
   openssl rand -base64 32
   ```

3. **Set secure GROQ_API_KEY** in `.env`

4. **Update FastAPI settings** in `app/main.py`:
   ```python
   app = FastAPI(docs_url=None, redoc_url=None)  # Disable swagger UI
   ```

### Deploy to Production

1. **Create .env on server with production values**

2. **Pull latest code**
   ```bash
   git clone <repo> && cd Chatapp
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Monitor with logs**
   ```bash
   docker-compose logs -f
   ```

### Backup Database

```bash
docker-compose exec postgres pg_dump -U postgres chatapp > backup.sql
```

### Restore Database

```bash
docker-compose exec -T postgres psql -U postgres chatapp < backup.sql
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use:

```bash
# Change in .env
APP_PORT=8001

# Or manually map a different port
docker-compose up -d
```

### Database Connection Failed

```bash
# Check database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Verify connection
docker-compose exec postgres psql -U postgres -d chatapp -c "SELECT 1;"
```

### Build Failed

```bash
# Clean and rebuild
docker-compose down
docker system prune -a
docker-compose up -d --build
```

### App Crashes on Startup

```bash
# View detailed logs
docker-compose logs app

# Check database migration
docker-compose exec app python -c "from app.database import Base; print('Database check ok')"
```

## Architecture

```
┌─────────────────────────────────────────────┐
│         Docker Network: chatapp_network      │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────────────┐  ┌──────────────────┐   │
│  │ FastAPI App  │  │   React SPA      │   │
│  │  (Port 8000) │  │   (Served by     │   │
│  │              │  │    FastAPI)      │   │
│  └──────────────┘  └──────────────────┘   │
│        │                                    │
│  ┌─────┴──────────────┬──────────────┐    │
│  │                    │              │    │
│  ▼                    ▼              ▼    │
│ ┌──────────┐    ┌────────────┐  ┌────┐  │
│ │PostgreSQL│    │   Redis    │  │API │  │
│ │Database  │    │   Cache    │  │    │  │
│ └──────────┘    └────────────┘  └────┘  │
│                                           │
└─────────────────────────────────────────────┘
```

## Health Checks

The app includes Docker health checks:

```bash
# Check health status
docker-compose ps

# The app container shows healthy/unhealthy status
```

Health checks verify:
- FastAPI app is running
- Endpoint is responding on port 8000

## Performance Optimization

For production deployments:

1. **Increase uvicorn workers** in Dockerfile
   ```dockerfile
   CMD ["python", "-m", "uvicorn", "app.main:rag_api", \
        "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
   ```

2. **Use production database settings**
   - Enable SSL connections
   - Set connection pooling

3. **Configure Redis caching**
   - Adjust max memory policy
   - Set eviction policy

4. **Use nginx reverse proxy** (optional)
   - Load balance multiple app containers
   - Handle SSL termination
   - Static file caching

## Monitoring

### View Resource Usage

```bash
docker stats
```

### Check Container Logs

```bash
docker-compose logs --tail=100 app
```

### Database Connections

```bash
docker-compose exec postgres psql -U postgres -d chatapp -c \
  "SELECT count(*) FROM pg_stat_activity;"
```

## Scaling

### Run Multiple App Instances

```yaml
version: '3.8'
services:
  app:
    # ... config ...
    deploy:
      replicas: 3
```

With nginx/load balancer frontend.

## Support

For issues with:
- **Docker build**: Check Dockerfile syntax and dependencies
- **Database**: Verify PostgreSQL is healthy (`docker-compose logs postgres`)
- **App startup**: Check logs for permission/connection issues
- **Frontend**: Verify React build completed successfully

