#!/bin/sh

# simple start script for now

function sigterm ()
{
  echo "Received SIGTERM, terminating task..."
  exit 0
}
trap sigterm SIGTERM


echo "Starting backend..."
npm run dev &

echo "Starting frontend..."
npm run react&
# add simple polling to check watch count
# [RELEASE][1] 0 rooms in batch
# [RELEASE][7] 1 rooms in batch

wait