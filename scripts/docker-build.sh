#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
TAG="${TAG:-$(git rev-parse --short HEAD 2>/dev/null || echo latest)}" docker compose -f docker-compose.yml build
