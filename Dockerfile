# podman build --tag tornado-object-storage:v1 .
# podman run --rm --interactive --tty --name object-storage tornado-object-storage:v1 /bin/sh
# podman run --rm --detach --tty --publish 8889:8888/tcp --name object-storage tornado-object-storage:v1
# Use a smaller image
FROM docker.io/library/alpine:latest

# Install the required Python modules
RUN apk add python3 py3-tornado

# Add the Python file to be used
COPY app.py /app.py
COPY cli.py /cli.py

# Add a user account
# No need to run as root in the container
RUN addgroup -S appgroup \
    && adduser -S appuser -G appgroup

# Run all future commands as appuser
USER appuser

# Set the command to run on start up
ENTRYPOINT ["python3", "/cli.py"]
