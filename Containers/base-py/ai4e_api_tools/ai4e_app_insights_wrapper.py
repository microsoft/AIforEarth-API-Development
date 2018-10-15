# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# This libary is used to wrap many of the Application Insights required objects
# into an easily usable package for Python.

from os import getenv
from ai4e_app_insights_context import AI4ETelemetryContext
from applicationinsights import TelemetryClient
from applicationinsights.channel import AsynchronousSender
from applicationinsights.channel import AsynchronousQueue
from applicationinsights.channel import TelemetryChannel

CONF_PREFIX = "APPINSIGHTS"
CONF_KEY_GRANTEE = CONF_PREFIX + "_INSTRUMENTATIONKEY"
CONF_KEY_AI4E = CONF_PREFIX + "_AI4E_INSTRUMENTATIONKEY"

class AI4EAppInsights(object):
    def __init__(self):
        self.grantee_key = getenv(CONF_KEY_GRANTEE, None)

        if (self.grantee_key):
            self.sender = AsynchronousSender()
            self.r_queue = AsynchronousQueue(self.sender)
            self.r_context = AI4ETelemetryContext()
            self.r_channel = TelemetryChannel(self.r_context, self.r_queue)

            self.appinsights_grantee_client = TelemetryClient(getenv(CONF_KEY_GRANTEE), self.r_channel)
            self.appinsights_ai4e_client = None

            if (getenv(CONF_KEY_AI4E)):
                self.appinsights_ai4e_client = TelemetryClient(getenv(CONF_KEY_AI4E), self.r_channel)

    def _log(self, message, sev, taskId = None, additionalProperties = None):
        if (self.grantee_key):
            if (taskId):
                if (additionalProperties is None):
                    additionalProperties = { 'task_id': taskId }
                else:
                    additionalProperties['task_id'] = taskId

            self.appinsights_grantee_client.track_trace(message, severity=sev, properties=additionalProperties)
            self.appinsights_grantee_client.flush()

            if (self.appinsights_ai4e_client):
                self.appinsights_ai4e_client.track_trace(message, severity=sev, properties=additionalProperties)
                self.appinsights_ai4e_client.flush()

    def log_debug(self, message, taskId = None, additionalProperties = None):
        self._log(message, "DEBUG", taskId, additionalProperties)

    def log_info(self, message, taskId = None, additionalProperties = None):
        self._log(message, "INFO", taskId, additionalProperties)

    def log_error(self, message, taskId = None, additionalProperties = None):
        self._log(message, "ERROR", taskId, additionalProperties)

    def log_warn(self, message, taskId = None, additionalProperties = None):
        self._log(message, "WARNING", taskId, additionalProperties)

    def log_exception(self, message, taskId = None, additionalProperties = None):
        self._log(message, "CRITICAL", taskId, additionalProperties)