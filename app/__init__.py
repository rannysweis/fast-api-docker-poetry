import os

if os.environ.get("OTEL_SERVICE_NAME"):
    import opentelemetry.instrumentation.auto_instrumentation.sitecustomize as autotrace
