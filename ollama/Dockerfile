FROM ollama/ollama:latest

# Install curl
RUN apt-get update && apt-get install -y curl

# Copy the start.sh script
COPY start.sh /start.sh

# Make sure the script is executable
RUN chmod +x /start.sh

# Use shell form to execute the start.sh script
ENTRYPOINT ["/bin/bash", "/start.sh"]
