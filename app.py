from flask import Flask, jsonify
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST
)

import time
from functools import wraps
import os

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of requests",
    ["method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Request latency in seconds",
    ["endpoint"]
)


def track_metrics(endpoint_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status_code = 200
            try:
                response = func(*args, **kwargs)
                return response
            except Exception:
                status_code = 500
                REQUEST_COUNT.labels(
                    method="GET",
                    endpoint=endpoint_name,
                    http_status=str(status_code)
                ).inc()
                raise
            finally:
                latency = time.time() - start_time
                REQUEST_LATENCY.labels(endpoint=endpoint_name).observe(latency)
                REQUEST_COUNT.labels(
                    method="GET",
                    endpoint=endpoint_name,
                    http_status=str(status_code)
                ).inc()
        return wrapper
    return decorator


@app.route("/")
@track_metrics("/")
def home():
    return jsonify({
        "message": "Hello from Flask DevOps sample app",
        "status": "success"
    })


@app.route("/health")
@track_metrics("/health")
def health():
    return jsonify({
        "status": "healthy",
        "app_name": os.getenv("APP_NAME", "devops-sample-app")
    })


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
