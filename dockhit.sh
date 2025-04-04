#!/bin/bash

IMAGE_NAME="sast_runner:latest"
DOCKERFILE_PATH="."
SOURCE_LIST_DIR="/home/sourcelist"
OUTPUT_BASE="./results"

# Step 1: Build the Docker image
echo "Building Docker image..."
docker build -t "$IMAGE_NAME" "$DOCKERFILE_PATH" || exit 1

# Step 2: Iterate over all default_*.txt files
for LIST_FILE in "$SOURCE_LIST_DIR"/default_*.txt; do
    BASENAME=$(basename "$LIST_FILE" .txt)
    CONTAINER_NAME="scan_${BASENAME}"

    echo "Running scan for: $BASENAME"

    # Create container (do not start immediately)
    #docker create --name "$CONTAINER_NAME" "$IMAGE_NAME" bash
    docker run --name "$CONTAINER_NAME" -dit "$IMAGE_NAME"


    # Copy necessary files into container
    docker cp "$LIST_FILE" "$CONTAINER_NAME":/home/sourcelist/pack_list.txt
    docker cp ./pack_build.sh "$CONTAINER_NAME":/home/pack_build.sh
    docker cp ./scan.sh "$CONTAINER_NAME":/home/scan.sh

    # Start container (so that docker exec can run against a running container)
    #docker start "$CONTAINER_NAME"

    # Run both scripts in order using expect, wait for "FIN!"
    echo "Waiting for scan completion in container: $CONTAINER_NAME"
    expect <<EOF
      set timeout 15000
      log_user 1
      spawn docker exec --workdir /home "$CONTAINER_NAME" /bin/bash -c "./pack_build.sh && ./scan.sh"
      expect "FINSATT!"
EOF

    echo "Copying results from container..."

    # Copy results from container to host
    HOST_OUTPUT_DIR="$OUTPUT_BASE/$BASENAME"
    mkdir -p "$HOST_OUTPUT_DIR"
    docker cp "$CONTAINER_NAME":/home/output/. "$HOST_OUTPUT_DIR"

    echo "Results saved to: $HOST_OUTPUT_DIR"

    # Optional cleanup
    docker rm "$CONTAINER_NAME"

    #echo "Finished: $BASENAME"
    echo
done

echo "All scans completed! Combined results are in: $OUTPUT_BASE"
