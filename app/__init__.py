# from opentelemetry import trace
# from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
# from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
# from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
# from opentelemetry.sdk.resources import SERVICE_NAME, Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor
#
# # from app.main import fast_api_app
#
# resource = Resource(attributes={
#     SERVICE_NAME: "fastApiDockerPoetry-2"
# })
# provider = TracerProvider(resource=resource)
# provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))
# trace.set_tracer_provider(provider)
# SQLAlchemyInstrumentor().instrument()
