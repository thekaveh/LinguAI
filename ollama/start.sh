#!/bin/bash

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


# Split OLLAMA_MODELS into an array
IFS=' ' read -r -a image_array <<< "${OLLAMA_MODELS}"

# Debug: Print the entire array of models to be pulled
echo "Models to be pulled: ${image_array[*]}"
# Loop through the array and pull each image

for image in "${image_array[@]}"; do
    echo "Pulling image: $image"
    if ollama pull "$image"; then
        echo "$image successfully pulled."
    else
        echo "Failed to pull $image."
        exit 1
    fi
done

# Keep the container running by waiting on all background processes
wait