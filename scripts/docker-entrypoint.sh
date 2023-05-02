#!/bin/bash

set -e

# activate our virtual environment here
. /opt/pysetup/.venv/bin/activate

# Evaluating passed command:
exec "$@"