#!/usr/bin/env bash

COMPOSE_PROJECT_NAME=rmq_9b64
export COMPOSE_PROJECT_NAME

function build() {
    (
        cd test-container-py || exit 1
        docker build . -t rmq-test-py
    )
}

if [ "$1" == "build" ]; then
    build
    exit 0
fi

if [ "$1" == "up" ] || [ "$1" == "" ]; then
    build
    docker-compose up -d --remove-orphans
    exit 0
fi

docker-compose "$@"
