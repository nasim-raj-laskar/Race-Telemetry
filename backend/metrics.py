from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of inference requests"
)

INFERENCE_LATENCY = Histogram(
    "inference_latency_seconds",
    "Inference latency in seconds"
)

FEATURE_PSI = Gauge(
    "feature_psi",
    "PSI value for monitored features",
    ["feature"]
)

