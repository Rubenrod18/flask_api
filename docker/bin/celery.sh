#!/usr/bin/env bash

set -o errexit
set -o pipefail
set -o nounset

mkdir -p /var/run/celeryd
mkdir -p /var/log/celeryd

celery multi start ${CELERYD_NODES} \
    --workdir=${HOMEDIR} \
    --pidfile=/var/run/celeryd/%n.pid \
    --logfile=/var/log/celeryd/%n%I.log \
    --loglevel=DEBUG \
    --app=app.celery \
    ${CELERYD_OPTS//\"}

tail -F /var/log/celeryd/*.log
