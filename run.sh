#!/bin/sh

PYTHONASYNCIODEBUG=True \
  gunicorn \
  --log-config ./logging.conf \
  --bind 0.0.0.0:6789 \
  --reload \
  --workers 1 \
  --worker-class aiohttp.worker.GunicornUVLoopWebWorker \
  app.app:app