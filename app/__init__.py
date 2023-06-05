import logging

from app.config.settings import get_settings
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

settings = get_settings()
logger = logging.getLogger(__name__)

if settings.otel_service_name and settings.otel_exporter_otlp_endpoint:
    resource = Resource(attributes={
        SERVICE_NAME: settings.otel_service_name,
    })
    provider = TracerProvider(resource=resource, )
    exporter = OTLPSpanExporter(endpoint=settings.otel_exporter_otlp_endpoint)
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    import opentelemetry.instrumentation.auto_instrumentation.sitecustomize as autotrace  # NOQA
else:
    logger.info("OpenTelemetry trace/span exports are disabled")
