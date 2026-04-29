"""
backend/telemetry.py

Initialises OpenTelemetry tracing and exports spans to Jaeger via OTLP/gRPC.

Call setup_tracing() once at application startup (in main.py lifespan or
module level). After that, FastAPI requests are traced automatically via
the FastAPIInstrumentor.

Environment variables:
    OTEL_ENABLED          — set to "false" to disable tracing (default: true)
    OTEL_SERVICE_NAME     — service name shown in Jaeger (default: agentic-chess)
    OTEL_EXPORTER_OTLP_ENDPOINT — Jaeger OTLP gRPC endpoint
                                   (default: http://jaeger:4317)
"""

from __future__ import annotations

import os

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def setup_tracing(app) -> None:
    """
    Configure OpenTelemetry with a Jaeger OTLP exporter and instrument
    the given FastAPI app. Safe to call multiple times — skips setup
    if OTEL_ENABLED=false.
    """
    if os.environ.get("OTEL_ENABLED", "true").lower() == "false":
        print("[telemetry] Tracing disabled via OTEL_ENABLED=false")
        return

    service_name = os.environ.get("OTEL_SERVICE_NAME", "agentic-chess")
    endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://jaeger:4317")

    # Build a tracer provider scoped to this service
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # OTLP gRPC exporter → Jaeger
    exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    # Register as the global tracer provider
    trace.set_tracer_provider(provider)

    # Auto-instrument FastAPI routes — captures method, path, status code,
    # request duration, and any exceptions raised in route handlers
    FastAPIInstrumentor.instrument_app(app)

    # Auto-instrument httpx — traces any outbound HTTP calls (e.g. OpenAI)
    HTTPXClientInstrumentor().instrument()

    print(f"[telemetry] Tracing enabled -> service={service_name} endpoint={endpoint}")


def get_tracer(name: str = "agentic-chess"):
    """
    Return a named tracer for creating custom spans.

    Usage:
        tracer = get_tracer(__name__)
        with tracer.start_as_current_span("my-operation") as span:
            span.set_attribute("game_id", game_id)
            ...
    """
    return trace.get_tracer(name)