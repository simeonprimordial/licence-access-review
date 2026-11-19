
#!/bin/bash

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_DIR"

"$PROJECT_DIR/venv/bin/python" main.py
