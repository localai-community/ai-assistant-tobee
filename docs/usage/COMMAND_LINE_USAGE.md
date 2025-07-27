# LocalAI Community - Command Line Usage

The `start.sh` script now supports both interactive and command-line modes for maximum flexibility.

## Quick Reference

```bash
# Interactive menu (default)
./start.sh

# Direct commands
./start.sh gpu              # Start GPU setup
./start.sh nogpu            # Start no-GPU setup  
./start.sh stop             # Stop all services
./start.sh status           # Show system info
./start.sh debug            # Run diagnostics
./start.sh menu             # Show interactive menu

# With options
./start.sh gpu -y           # Auto-confirm all prompts
./start.sh nogpu --verbose  # Enable verbose output
./start.sh gpu --skip-checks # Skip compatibility checks
```

## Commands

### `gpu`
Start GPU-accelerated setup (macOS M1/M2 only)
- Uses native Apple Silicon GPU acceleration
- Installs Ollama on host system
- Maximum performance for M1/M2 Macs

### `nogpu` 
Start cross-platform no-GPU setup
- Works on Linux, Windows, Intel Macs
- Uses Docker Ollama (CPU only)
- Compatible with all platforms

### `stop`
Stop all running services
- Stops Docker containers
- Stops Ollama process
- Clean shutdown

### `status`
Show system information
- Operating system details
- Docker status
- Ollama status
- GPU availability

### `debug`
Run comprehensive diagnostics
- System compatibility check
- Service status verification
- Port availability check
- Component connectivity tests

### `menu`
Show interactive menu (default behavior)

## Options

### `-y, --yes`
Auto-confirm all prompts
- Skips user confirmation dialogs
- Useful for automated scripts
- Example: `./start.sh gpu -y`

### `-v, --verbose`
Enable verbose output
- Shows detailed progress information
- Useful for debugging
- Example: `./start.sh nogpu --verbose`

### `-q, --quiet`
Disable interactive mode
- Suppresses interactive prompts
- Useful for non-interactive environments
- Example: `./start.sh stop --quiet`

### `--skip-checks`
Skip system compatibility checks
- Bypasses platform verification
- Use with caution
- Example: `./start.sh gpu --skip-checks`

### `-h, --help`
Show help message
- Displays usage information
- Lists all available commands and options

## Examples

### Basic Usage
```bash
# Start with interactive menu
./start.sh

# Quick GPU setup
./start.sh gpu

# Quick no-GPU setup
./start.sh nogpu

# Stop everything
./start.sh stop
```

### Advanced Usage
```bash
# Auto-confirm GPU setup
./start.sh gpu -y

# Verbose no-GPU setup
./start.sh nogpu --verbose

# Skip checks for GPU setup
./start.sh gpu --skip-checks

# Check system status
./start.sh status

# Run diagnostics
./start.sh debug
```

### Automation Examples
```bash
#!/bin/bash
# Automated setup script

# Check system status first
./start.sh status

# Start appropriate setup based on platform
if [[ "$OSTYPE" == "darwin"* ]] && [[ $(uname -m) == "arm64" ]]; then
    ./start.sh gpu -y --skip-checks
else
    ./start.sh nogpu -y
fi

# Wait for services to be ready
sleep 10

# Run diagnostics
./start.sh debug
```

### CI/CD Integration
```bash
# In CI/CD pipeline
./start.sh nogpu -y --quiet
./start.sh status
./start.sh debug
# Run tests...
./start.sh stop
```

## Error Handling

The script provides clear error messages and exit codes:

- `0`: Success
- `1`: General error
- `2`: Invalid arguments
- `3`: System compatibility error

## Tips

1. **Use `-y` for automation**: Always use `-y` flag in scripts to avoid hanging on prompts
2. **Check status first**: Run `./start.sh status` to verify system readiness
3. **Debug issues**: Use `./start.sh debug` to diagnose problems
4. **Clean shutdown**: Always use `./start.sh stop` to properly clean up services
5. **Verbose mode**: Use `--verbose` when troubleshooting setup issues

## Migration from Old Usage

The script maintains backward compatibility:

```bash
# Old way (still works)
./start.sh

# New way (more flexible)
./start.sh menu
./start.sh gpu
./start.sh nogpu
./start.sh stop
``` 