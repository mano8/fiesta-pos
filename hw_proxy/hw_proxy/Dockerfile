# Use Python 3.11 slim base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    # Add the local user's bin directory to PATH
    PATH="/home/appuser/.local/bin:$PATH"

# Create a non-root user and group
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --create-home appuser

# Set working directory
WORKDIR /opt

# Install build dependencies if needed (e.g., for any compiled packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    dos2unix \
    python3-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create the app directories and set permissions
RUN mkdir -p ./hw_proxy \
    && chown -R appuser:appuser ./hw_proxy

# Copy requirements and install them as the non-root user
COPY --chown=appuser:appuser ./hw_proxy/requirements-docker-dev.txt .

# Switch to the non-root user
USER appuser

# Install Python dependencies
# Use --no-cache-dir to avoid caching the packages in the image
# Use --user to install packages in the user's home directory
RUN pip install --no-cache-dir --user --upgrade pip && \
    pip install --no-cache-dir --user -r requirements-docker-dev.txt

# Copy the hw_proxy source code
COPY --chown=appuser:appuser ./hw_proxy ./hw_proxy

RUN dos2unix /opt/hw_proxy/scripts/docker_start.sh

# Ensure scripts have execution permission
RUN chmod +x /opt/hw_proxy/scripts/docker_start.sh

RUN ls -alt /opt/hw_proxy/scripts/

# Set the PYTHONPATH to ensure the hw_proxy module is found
ENV PYTHONPATH=/opt/hw_proxy

# Expose FastAPI port (use 8015)
EXPOSE 8015

# Use the entrypoint script as CMD, which will run migrations and then launch uvicorn
CMD ["/opt/hw_proxy/scripts/docker_start.sh"]