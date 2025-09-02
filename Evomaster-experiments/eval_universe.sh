#!/bin/bash

# Define the URL
url="https://www.universe.com/graphql"

# Define the different max times to test
times=(
    "5s"
    "10s"
    "20s"
    "30s"
    "60s"
)

# Loop through each time duration
for max_time in "${times[@]}"; do
    echo "Processing $url with max time: $max_time"

    # Run EvoMaster with current time configuration
    java -jar evomaster.jar \
        --blackBox true \
        --bbTargetUrl "$url" \
        --problemType GRAPHQL \
        --outputFormat JAVA_JUNIT_4 \
        --maxTime "$max_time"

    # Create folder name with the time duration
    folder_name="universe-${max_time}-src"

    # Move the generated source to the new folder
    if [ -d "src/em" ]; then
        mv src/em "$folder_name"
        echo "Moved output to $folder_name"
    else
        echo "Warning: src/em directory not found for $max_time run"
    fi
done
