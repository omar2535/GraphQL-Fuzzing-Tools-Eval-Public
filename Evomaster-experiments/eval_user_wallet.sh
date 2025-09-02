#!/usr/bin/env bash
set -Eeuo pipefail

# Config
url="http://localhost:4000/graphql"
times=("5s" "10s" "20s" "30s" "60s")
num_experiments=20

# Base output directory for this batch
outdir="runs_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$outdir"

for max_time in "${times[@]}"; do
  for exp in $(seq 1 "$num_experiments"); do
    echo "[$(date +%T)] Processing $url with max time: $max_time (experiment $exp/$num_experiments)"

    # Clean previous artifacts so runs don't mix
    rm -rf generated_tests || true

    # Optional: seed for reproducible randomness (uncomment if supported by your evomaster build)
    # seed=$(( (RANDOM<<16) ^ (RANDOM<<1) ^ exp ))

    # Run EvoMaster
    java -jar evomaster.jar \
      --blackBox true \
      --bbTargetUrl "$url" \
      --problemType GRAPHQL \
      --outputFormat JAVA_JUNIT_4 \
      --maxTime "$max_time"
      # --seed "$seed"

    # Move only *.java files from generated_tests to the run folder (preserve dir structure)
    if [ -d "generated_tests" ]; then
      dest="${outdir}/user-wallet-${max_time}-exp$(printf '%02d' "$exp")-src"
      mkdir -p "$dest"

      # Copy only .java files while keeping directories, then delete originals (net effect: move)
      rsync -a -m \
        --include='*/' \
        --include='*.java' \
        --exclude='*' \
        "generated_tests/" "$dest/"

      count=$(find "$dest" -type f -name '*.java' | wc -l | tr -d ' ')
      if [ "$count" -gt 0 ]; then
        # Remove the .java files we just copied, leaving any non-java artifacts untouched
        find "generated_tests" -type f -name '*.java' -delete
        echo "  Moved $count .java files to $dest"
      else
        echo "  Warning: no .java files found under generated_tests for this run"
      fi
    else
      echo "  Warning: generated_tests directory not found for $max_time (experiment $exp)"
    fi
  done
done

echo "All done. Outputs saved under: $outdir"
