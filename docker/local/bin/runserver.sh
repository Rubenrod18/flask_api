#!/usr/bin/env bash

set -o errexit
# This causes the script to exit immediately if any command returns a non-zero exit status (an error).
# It helps prevent the script from continuing after encountering an error.

set -o pipefail
# Normally, in a pipeline (e.g, command1 | command2), only the exit status of the last command (command2) is considered.
# With pipefail, the pipeline will return the exit status of the first command that fails, making it easier to catch
# errors in complex pipelines.

set -o nounset
# This makes the script treat the use of unset variables as an error.
# If the script tries to use an undefined variable, it will immediately exit with an error, preventing subtle bugs.

flask create_db
flask db upgrade --directory "$MIGRATIONS_DIR"
flask run --host 0.0.0.0 --debug
