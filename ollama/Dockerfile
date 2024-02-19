FROM ollama/ollama:latest

# Install curl
RUN apt-get update && apt-get install -y curl

# Copy the start.sh script
COPY start.sh /start.sh
# COPY ../.env /.env  # This assumes Dockerfile is in the same directory as start.sh

# Make sure the script is executable
RUN chmod +x /start.sh

# Use shell form to execute the start.sh script
ENTRYPOINT ["/bin/bash", "/start.sh"]