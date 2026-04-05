from functools import wraps
import os
import time

from flask import Flask, jsonify
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Histogram,
    generate_latest,
)

app = Flask(__name__)

REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Latency of HTTP requests in seconds",
    ["endpoint"],
)


def monitor(endpoint_name):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "200"
            method = "GET"
            try:
                response = func(*args, **kwargs)
                return response
            except Exception:
                status = "500"
                raise
            finally:
                duration = time.time() - start_time
                REQUEST_COUNT.labels(
                    method=method,
                    endpoint=endpoint_name,
                    status=status,
                ).inc()
                REQUEST_LATENCY.labels(endpoint=endpoint_name).observe(
                    duration
                )

        return wrapper

    return decorator


@app.route("/")
@monitor("/")
def home():
    return jsonify(
        {
            "message": "Hello from Flask DevOps sample app",
            "status": "success",
        }
    )


@app.route("/health")
@monitor("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
            "app_name": os.getenv(
                "APP_NAME",
                "devops-sample-app",
            ),
        }
    )


@app.route("/about")
@monitor("/about")
def about():
    return jsonify(
        {
            "project": "DEVOPS-DEPLOYED",
            "stack": [
                "Flask",
                "Docker",
                "Prometheus",
                "Grafana",
                "Ansible",
                "GitHub Actions",
            ],
        }
    )


@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {
        "Content-Type": CONTENT_TYPE_LATEST,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
