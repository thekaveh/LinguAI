# This script starts the Ollama service and pulls the specified models.
# It loads environment variables from the .env file, starts the Ollama service in the background,
# and waits for it to be ready. Then, it splits the DOCKER_IMAGES variable into an array and
# pulls each image using the "ollama pull" command. Finally, it keeps the container running by
# waiting on all background processes.

echo "Starting Ollama service..."
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


# Split DOCKER_IMAGES into an array
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