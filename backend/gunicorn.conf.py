from __future__ import annotations

import multiprocessing

bind = "0.0.0.0:5000"
worker_class = "gevent"
workers = multiprocessing.cpu_count() * 2 + 1
worker_connections = 1000
timeout = 60
graceful_timeout = 30
keepalive = 5
accesslog = "-"
errorlog = "-"
capture_output = True
loglevel = "info"
max_requests = 1000
max_requests_jitter = 100

