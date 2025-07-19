# LocalAI Community - Troubleshooting Guide

## Common Issues and Solutions

### 1. "No models available" Warning

**Problem**: The frontend shows "No models available - Please make sure Ollama is running and models are installed."

**Solution**: 
1. Check if Ollama is running: `docker ps | grep ollama`
2. Download a model: `docker exec localaicommunity-ollama-1 ollama pull llama3.2:latest`
3. Verify models: `curl http://localhost:11434/api/tags`

### 2. Backend Returns 405 Error

**Problem**: Backend returns "405 Method Not Allowed" when sending chat requests.

**Solution**: 
1. Check if the backend URL is correct in the frontend configuration
2. Ensure the backend is running: `docker ps | grep backend`
3. Test the backend directly: `curl http://localhost:8001/health`

### 3. Backend Can't Connect to Ollama

**Problem**: Backend shows "Ollama service is not available" in health checks.

**Solution**:
1. Verify Ollama is running: `docker ps | grep ollama`
2. Check if models are downloaded: `curl http://localhost:11434/api/tags`
3. Restart the backend: `docker-compose restart backend`

### 4. Frontend Can't Connect to Backend

**Problem**: Frontend shows connection errors to the backend.

**Solution**:
1. Check if the backend URL is correct (should be `http://backend:8001` in Docker)
2. Verify both services are running: `docker ps`
3. Check backend logs: `docker logs localaicommunity-backend-1`

## Quick Start Commands

### Start Everything
```bash
./start.sh
```

### Manual Start
```bash
# Start services
docker-compose up -d

# Download model (if needed)
docker exec localaicommunity-ollama-1 ollama pull llama3.2:latest

# Check status
docker ps
curl http://localhost:8001/api/v1/chat/health
```

### Stop Everything
```bash
docker-compose down
```

## Service URLs

- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:8001
- **Ollama**: http://localhost:11434

## Health Checks

```bash
# Check Ollama
curl http://localhost:11434/api/tags

# Check Backend
curl http://localhost:8001/health
curl http://localhost:8001/api/v1/chat/health

# Check Frontend
curl http://localhost:8000/health
```

## Logs

```bash
# View all logs
docker-compose logs

# View specific service logs
docker logs localaicommunity-backend-1
docker logs localaicommunity-frontend-1
docker logs localaicommunity-ollama-1
``` 