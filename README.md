An application built with Python and the Tornado Web framework providing access to an object storage service using the AWSv4 signed URL signature.

    docker pull ghcr.io/kyoobit/tornado-object-storage:latest
    docker run -d ghcr.io/kyoobit/tornado-object-storage:latest \
    --key ${ACCESS_ID} --secret ${ACCESS_SECRET} \
    --publish 8888:8888 tornado-object-storage
