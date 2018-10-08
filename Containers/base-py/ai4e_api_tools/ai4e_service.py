# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from threading import Thread
from os import getenv
from opencensus.trace.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.tracer import Tracer
from opencensus.trace.exporters.ocagent import trace_exporter
from opencensus.trace.exporters.transports.background_thread import BackgroundThreadTransport

# Use OpenCensus to send traces to Application Insights
export_LocalForwarder = trace_exporter.TraceExporter(
    transport=BackgroundThreadTransport,
    service_name=getenv("SERVICE_OWNER", "Default") + ":" + getenv("SERVICE_MODEL_NAME", "Default"),
    endpoint=getenv('OCAGENT_TRACE_EXPORTER_ENDPOINT'))
tracer = Tracer(exporter=export_LocalForwarder)

class AI4EWrapper():
    def __init__(self, api_app):
        self.middleware = FlaskMiddleware(api_app)

    def wrap_sync_endpoint(self, func, trace_name, **kwargs):
         with tracer.span(name=trace_name) as span:
            return func(**kwargs)

    def wrap_async_endpoint(self, func, trace_name=None, **kwargs):
        if (trace_name):
            with tracer.span(name=trace_name) as span:
                self._create_and_execute_thread(func, **kwargs)
        else:
            self._create_and_execute_thread(func, **kwargs)

    def _create_and_execute_thread(self, func, **kwargs):
        thread = Thread(target = func, kwargs = kwargs)
        thread.start()