# podman build --tag tornado-object-storage:v1 .
# podman run --rm --interactive --tty --name object-storage tornado-object-storage:v1 /bin/sh
# podman run --rm --detach --tty --publish 8889:8888/tcp --name object-storage tornado-object-storage:v1
FROM docker.io/library/python:slim

# Install system dependencies
#RUN apt-get update && apt-get install -y \
#    some-package \
#    && rm -rf /var/lib/apt/lists/*

# Add the appuser account
RUN adduser --disabled-password --disabled-login --no-create-home appuser

# Set the working directory to /app
WORKDIR /app

# Install uv using the official installer
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Add the Python files for the application
COPY pyproject.toml uv.lock README.md src/*.py ./

# Create additional directories and set permissions
RUN mkdir -p /app/.cache && \
    chown -R appuser:appuser /app

# Set uv to use the .cache directory
ENV UV_CACHE_DIR=/app/.cache/uv

# Install Python dependencies
RUN uv sync --frozen --no-cache

# No need to run as root in the container
USER appuser

# Set the command to run on start up
ENTRYPOINT ["uv", "run",  "/app/cli.py"]
#CMD ["--help"]
