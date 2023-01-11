#!/bin/bash

set -eou pipefail

version='latest' #$(<"./.HA_VERSION")
docker pull -q "ghcr.io/home-assistant/home-assistant:${version}"

docker run --rm \
        --entrypoint "" \
        "ghcr.io/home-assistant/home-assistant:${version}" \
        python -m homeassistant --version
    env_file_arg=""
    docker run --rm \
        --entrypoint "" \
        -v $(pwd):/github/workspace \
        -v $(pwd)/travis_secrets.yaml:/github/workspace/secrets.yaml \
        --workdir /github/workspace \
        "ghcr.io/home-assistant/home-assistant:${version}" \
        python -m homeassistant \
            --config "." \
            --script check_config
