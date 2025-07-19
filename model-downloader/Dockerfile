FROM alpine:latest

# Install curl and other necessary tools
RUN apk add --no-cache curl

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Set the entrypoint to ollama
ENTRYPOINT ["/usr/local/bin/ollama"] 