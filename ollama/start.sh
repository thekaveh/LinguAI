#!/bin/bash
# Start Ollama service in the background
ollama serve &

# Function to check if Ollama is running
check_ollama_running() {
    if curl -s http://localhost:11434 | grep -q "Ollama is running"; then
        return 0
    else
        return 1
    fi
}

# Wait for Ollama to be ready
echo "Waiting for Ollama service to be ready..."
until check_ollama_running; do
    sleep 1
    echo -n "."
done
echo "Ollama service is ready."

# Pull the specified models
ollama pull llama2:latest
ollama pull mistral:latest

# Keep the container running by waiting on all background processes
wait
