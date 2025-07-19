# LocalAI Community - GPU Setup Guide

## 🚀 Quick Start with GPU

### One-Command GPU Setup
```bash
./run-with-gpu.sh
```

This script will:
- ✅ Install Ollama with GPU support
- ✅ Download models automatically
- ✅ Start all services with GPU acceleration
- ✅ Test the setup
- ✅ Monitor performance

### Stop GPU Services
```bash
./stop-gpu.sh
```

## 🍎 macOS M1/M2 GPU Support

### Why GPU Acceleration?
- **10-50x faster** than CPU-only inference
- **Lower latency** for real-time chat
- **Better performance** for complex tasks
- **Automatic optimization** for Apple Silicon

### How It Works
1. **Ollama runs natively** on macOS (not in Docker)
2. **M2 GPU** is automatically detected and used
3. **Backend/Frontend** run in Docker containers
4. **Network bridge** connects Docker to host Ollama

## 📊 Performance Comparison

| Setup | GPU Access | Speed | Memory | Use Case |
|-------|------------|-------|--------|----------|
| **Docker CPU** | ❌ No | ~5-15 tokens/s | Higher | Cross-platform |
| **Host GPU** | ✅ Yes | ~50-200 tokens/s | Lower | Mac optimization |

## 🔧 Manual Setup (Alternative)

### Step 1: Install Ollama
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Download Models
```bash
# General purpose
ollama pull llama3:latest

# Smaller, faster
ollama pull llama3.2:latest

# Code assistance
ollama pull codellama:7b

# High performance
ollama pull mistral:latest
```

### Step 3: Start Ollama
```bash
ollama serve
```

### Step 4: Start Services
```bash
docker-compose -f docker-compose.host-ollama.yml up -d
```

## 📱 Access Points

- **Frontend**: http://localhost:8000
- **Backend API**: http://localhost:8001
- **Ollama API**: http://localhost:11434

## 🔍 Monitoring GPU Usage

### Activity Monitor
1. Open **Activity Monitor**
2. Go to **GPU** tab
3. Look for **ollama** processes
4. Monitor **GPU usage** percentage

### Terminal Monitoring
```bash
# Check Ollama processes
ps aux | grep ollama

# Check GPU layers
ps aux | grep ollama | grep -o '--n-gpu-layers [0-9]*'

# Monitor in real-time
watch -n 1 'ps aux | grep ollama'
```

### Performance Testing
```bash
# Test response time
time ollama run llama3:latest "Hello, world!"

# Test with longer prompt
ollama run llama3:latest "Write a 100-word story about a robot learning to paint"
```

## 🛠️ Troubleshooting

### GPU Not Detected
```bash
# Check Apple Silicon
uname -m  # Should show "arm64"

# Check GPU info
system_profiler SPDisplaysDataType

# Reinstall Ollama
curl -fsSL https://ollama.ai/install.sh | sh
```

### Services Not Starting
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
pkill ollama
ollama serve

# Check Docker containers
docker ps
```

### Performance Issues
```bash
# Check available memory
top -l 1 | grep PhysMem

# Check CPU usage
top -l 1 | grep CPU

# Restart with fresh environment
./stop-gpu.sh
./run-with-gpu.sh
```

## 📋 Available Models

### Recommended Models for M2
1. **llama3:latest** (4.7GB) - Best general performance
2. **llama3.2:latest** (2.0GB) - Faster, smaller
3. **codellama:7b** (4.0GB) - Code assistance
4. **mistral:latest** (4.1GB) - High performance

### Model Management
```bash
# List installed models
ollama list

# Remove model
ollama rm llama3:latest

# Update model
ollama pull llama3:latest
```

## 🔒 Security & Privacy

### Local Processing
- ✅ **All data stays on your Mac**
- ✅ **No internet required** after setup
- ✅ **No data sent to external services**
- ✅ **Complete privacy** guaranteed

### Resource Usage
- **GPU**: Automatically managed by Ollama
- **Memory**: ~4-8GB for typical models
- **Storage**: ~2-5GB per model
- **CPU**: Minimal usage with GPU acceleration

## 🎯 Best Practices

### For Maximum Performance
1. **Close other GPU-intensive apps** (games, video editing)
2. **Use SSD storage** for faster model loading
3. **Keep 8GB+ free RAM** for optimal performance
4. **Monitor Activity Monitor** for resource usage

### For Development
1. **Use smaller models** for faster iteration
2. **Test with different models** for your use case
3. **Monitor logs** for debugging
4. **Use the stop script** to clean up resources

## 🚀 Advanced Configuration

### Custom Ollama Settings
```bash
# Start with custom parameters
ollama serve --host 0.0.0.0 --port 11434

# Set environment variables
export OLLAMA_HOST=0.0.0.0
export OLLAMA_KEEP_ALIVE=24h
```

### Docker Configuration
```yaml
# In docker-compose.host-ollama.yml
environment:
  - OLLAMA_URL=http://host.docker.internal:11434
extra_hosts:
  - "host.docker.internal:host-gateway"
```

## 📞 Support

### Common Issues
- **Port conflicts**: Change ports in docker-compose
- **Memory issues**: Use smaller models
- **Performance**: Check GPU usage in Activity Monitor
- **Network**: Ensure Docker can reach host

### Getting Help
1. Check this documentation
2. Review `docs/TROUBLESHOOTING.md`
3. Check logs: `docker-compose logs -f`
4. Monitor system resources

---

**🎉 Enjoy your GPU-accelerated AI assistant!** 