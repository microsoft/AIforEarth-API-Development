# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# This is a wrapper on top of the normal Application Insights Python SDKs.
# The only addition is an AI4E instrumentation key that only gets added
# when the service is hosted by Microsoft in our AI for Earth API system.

from os import getenv
import socket

from applicationinsights import TelemetryClient
from applicationinsights.channel import AsynchronousSender
from applicationinsights.channel import AsynchronousQueue
from applicationinsights.channel import TelemetryChannel
from applicationinsights.logging import LoggingHandler
from applicationinsights.requests import WSGIApplication

from ai4e_app_insights_context import AI4ETelemetryContext


CONF_PREFIX = "APPINSIGHTS"

CONF_KEY_GRANTEE = CONF_PREFIX + "_INSTRUMENTATIONKEY"
CONF_KEY_AI4E = CONF_PREFIX + "_AI4E_INSTRUMENTATIONKEY"
CONF_ENDPOINT_URI = CONF_PREFIX + "_ENDPOINT_URI"
CONF_DISABLE_REQUEST_LOGGING = CONF_PREFIX + "_DISABLE_REQUEST_LOGGING"
CONF_DISABLE_TRACE_LOGGING = CONF_PREFIX + "_DISABLE_TRACE_LOGGING"
CONF_DISABLE_EXCEPTION_LOGGING = CONF_PREFIX + "_DISABLE_EXCEPTION_LOGGING"


class AppInsights(object):
    """ This class represents a Flask extension that enables request telemetry,
    trace logging and exception logging for a Flask application. The telemetry
    will be sent to Application Insights service using the supplied
    instrumentation key.

    The following Flask config variables can be used to configure the extension:

    - Set ``APPINSIGHTS_INSTRUMENTATIONKEY`` to a string to provide the
      instrumentation key to send telemetry to application insights.
      Alternatively, this value can also be provided via an environment variable
      of the same name.

    - Set ``APPINSIGHTS_ENDPOINT_URI`` to a string to customize the telemetry
      endpoint to which Application Insights will send the telemetry.

    - Set ``APPINSIGHTS_DISABLE_REQUEST_LOGGING`` to ``False`` to disable
      logging of Flask requests to Application Insights.

    - Set ``APPINSIGHTS_DISABLE_TRACE_LOGGING`` to ``False`` to disable logging
      of all log traces to Application Insights.

    - Set ``APPINSIGHTS_DISABLE_EXCEPTION_LOGGING`` to ``False`` to disable
      logging of all exceptions to Application Insights.

    .. code:: python

            from flask import Flask
            from ai4e_app_insights import AppInsights

            # instantiate the Flask application
            app = Flask(__name__)
            app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = '<YOUR INSTRUMENTATION KEY GOES HERE>'

            # log requests, traces and exceptions to the Application Insights service
            appinsights = AppInsights(app)

            # define a simple route
            @app.route('/')
            def hello_world():
                return 'Hello World!'

            # run the application
            if __name__ == '__main__':
                app.run()
    """
    def __init__(self, app=None, context=None):
        """
        Initialize a new instance of the extension.

        Args:
            app (flask.Flask). the Flask application for which to initialize the extension.
        """
        socket.setdefaulttimeout(30)
        self._key_grantee = None
        self._key_ai4e = None
        self._endpoint_uri = None
        self._channel = None
        self._requests_middleware = None
        self._trace_log_handler_grantee = None
        self._trace_log_handler_ai4e = None
        self._exception_telemetry_client_grantee = None
        self._exception_telemetry_client_ai4e = None

        if app:
            self.init_app(app, context)

    def init_app(self, app, context):
        """
        Initializes the extension for the provided Flask application.

        Args:
            app (flask.Flask). the Flask application for which to initialize the extension.
        """
        print("Starting application insights module.")
        self._key_grantee = app.config.get(CONF_KEY_GRANTEE) or getenv(CONF_KEY_GRANTEE)
        self._key_ai4e = app.config.get(CONF_KEY_AI4E) or getenv(CONF_KEY_AI4E)

        if (self._key_grantee and len(self._key_grantee.strip()) > 0):
            self._key_grantee = self._key_grantee.strip()
        else:
            self._key_grantee = None
        
        if (self._key_ai4e and len(self._key_ai4e.strip()) > 0):
            self._key_ai4e = self._key_ai4e.strip()
        else:
            self._key_ai4e = None

        if self._key_grantee:
            print("Grantee application insights key set.")

        if self._key_ai4e:
            print("AI4E application insights key set: " + str(self._key_ai4e))

        if not self._key_grantee and not self._key_ai4e:
            return

        self._endpoint_uri = app.config.get(CONF_ENDPOINT_URI)

        if self._endpoint_uri:
            sender = AsynchronousSender(self._endpoint_uri)
        else:
            sender = AsynchronousSender()

        queue = AsynchronousQueue(sender)

        if not context:
            context = AI4ETelemetryContext()

        self._channel = TelemetryChannel(context, queue)

        self._init_request_logging(app)
        self._init_trace_logging(app)
        self._init_exception_logging(app)

    def _init_request_logging(self, app):
        """
        Sets up request logging unless ``APPINSIGHTS_DISABLE_REQUEST_LOGGING``
        is set in the Flask config.

        Args:
            app (flask.Flask). the Flask application for which to initialize the extension.
        """
        enabled = not app.config.get(CONF_DISABLE_REQUEST_LOGGING, False)

        if not enabled:
            return

        # If in the AI4E backend, only send uwsgi traces to AI4E
        wsgi_key = self._key_ai4e
        if not wsgi_key:
            wsgi_key = self._key_grantee

        self._requests_middleware = WSGIApplication(
            wsgi_key, app.wsgi_app, telemetry_channel=self._channel)

        app.wsgi_app = self._requests_middleware

    def _init_trace_logging(self, app):
        """
        Sets up trace logging unless ``APPINSIGHTS_DISABLE_TRACE_LOGGING`` is
        set in the Flask config.

        Args:
            app (flask.Flask). the Flask application for which to initialize the extension.
        """
        enabled = not app.config.get(CONF_DISABLE_TRACE_LOGGING, False)

        if not enabled:
            return

        if self._key_grantee:
            self._trace_log_handler_grantee = LoggingHandler(
                self._key_grantee, telemetry_channel=self._channel)

            app.logger.addHandler(self._trace_log_handler_grantee)

        if self._key_ai4e:
            print("Starting trace logging")
            self._trace_log_handler_ai4e = LoggingHandler(
                self._key_ai4e, telemetry_channel=self._channel)

            app.logger.addHandler(self._trace_log_handler_ai4e)

    def _init_exception_logging(self, app):
        """
        Sets up exception logging unless ``APPINSIGHTS_DISABLE_EXCEPTION_LOGGING``
        is set in the Flask config.

        Args:
            app (flask.Flask). the Flask application for which to initialize the extension.
        """
        enabled = not app.config.get(CONF_DISABLE_EXCEPTION_LOGGING, False)

        if not enabled:
            return

        if self._key_grantee:
            self._exception_telemetry_client_grantee = TelemetryClient(
                self._key_grantee, telemetry_channel=self._channel)

        if self._key_ai4e:
            self._exception_telemetry_client_ai4e = TelemetryClient(
                self._key_ai4e, telemetry_channel=self._channel)


        @app.errorhandler(Exception)
        def exception_handler(exception):
            try:
                raise exception
            except Exception:
                if self._exception_telemetry_client_grantee:
                    self._exception_telemetry_client_grantee.track_exception()

                if self._exception_telemetry_client_ai4e:
                    self._exception_telemetry_client_ai4e.track_exception()
            finally:
                raise exception

    def flush(self):
        """Flushes the queued up telemetry to the service.
        """
        print("trying all flush")
        if self._requests_middleware:
            self._requests_middleware.flush()

        if self._trace_log_handler_grantee:
            self._trace_log_handler_grantee.flush()

        if self._trace_log_handler_ai4e:
            print("Trying trace flush...")
            self._trace_log_handler_ai4e.flush()
            print("Trace flush finsihed.")

        if self._exception_telemetry_client_grantee:
            self._exception_telemetry_client_grantee.flush()

        if self._exception_telemetry_client_ai4e:
            self._exception_telemetry_client_ai4e.flush()
