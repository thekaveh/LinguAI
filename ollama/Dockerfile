# Pin to a specific Ollama runtime version so model-format changes upstream
# don't silently break the deployment. Bump intentionally when validating a
# newer Ollama release.
FROM ollama/ollama:0.4.3

# Single apt-get layer: update + install + clean. `apt-get install` without
# `apt-get update` would either fail on a fresh base or pull from stale lists.
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
        tzdata \
        postgresql-client && \
    ln -snf /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo America/New_York > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Copy the start.sh script and normalize line endings (Windows checkouts may
# introduce CRLF and bash will reject the shebang).
COPY start.sh /start.sh
RUN sed -i 's/\r$//' /start.sh && chmod +x /start.sh

ENTRYPOINT ["/bin/bash", "/start.sh"]
