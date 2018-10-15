# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import platform
import locale
from os import getenv
from applicationinsights.channel import contracts

CONF_SERVICE_OWNER = "SERVICE_OWNER"
CONF_SERVICE_NAME = "SERVICE_NAME"
CONF_SERVICE_VERSION = "SERVICE_VERSION"
CONF_SERVICE_CLUSTER = "SERVICE_CLUSTER"
CONF_SERVICE_MODEL_NAME = "SERVICE_MODEL_NAME"
CONF_SERVICE_MODEL_FRAMEWORK = "SERVICE_MODEL_FRAMEWORK"
CONF_SERVICE_MODEL_FRAMEOWRK_VERSION = "SERVICE_MODEL_FRAMEOWRK_VERSION"
CONF_SERVICE_MODEL_VERSION = "SERVICE_MODEL_VERSION"
CONF_SERVICE_CONTAINER_VERSION = "SERVICE_CONTAINER_VERSION"
CONF_SERVICE_CONTAINER_NAME = "SERVICE_CONTAINER_NAME"

# save off whatever is currently there
existing_device_initialize = contracts.Device._initialize
def device_initialize(self):
    """ The device initializer used to assign special properties to all device context objects"""
    existing_device_initialize(self)
    self.type = 'Other'
    self.id = platform.node()
    self.os_version = platform.version()
    self.locale = locale.getdefaultlocale()[0]

# assign the device context initializer
contracts.Device._initialize = device_initialize

class AI4ETelemetryContext(object):
    """Represents the context for sending telemetry to the Application Insights service.
    """
    def __init__(self):
        """Initializes a new instance of the class.
        """
        self.type = 'Service'
        self.platform_node = platform.node()
        self.platform_os_version = platform.version()
        self.platform_locale = locale.getdefaultlocale()[0]
        self.platform_processor = platform.processor()
        self.platform_python_version = platform.python_version()

        self.device = contracts.Device()
        self.cloud = contracts.Cloud()
        self.application = contracts.Application()
        self.user = contracts.User()
        self.session = contracts.Session()
        self.operation = contracts.Operation()
        self.location = contracts.Location()

        self.service_owner = getenv(CONF_SERVICE_OWNER)
        self.service_name = getenv(CONF_SERVICE_NAME)
        self.service_version = getenv(CONF_SERVICE_VERSION)
        self.service_cluster = getenv(CONF_SERVICE_CLUSTER)
        self.service_model_name = getenv(CONF_SERVICE_MODEL_NAME)
        self.service_model_framework = getenv(CONF_SERVICE_MODEL_FRAMEWORK)
        self.service_model_framework_version = getenv(CONF_SERVICE_MODEL_FRAMEOWRK_VERSION)
        self.service_model_version = getenv(CONF_SERVICE_MODEL_VERSION)
        self.service_container_version = getenv(CONF_SERVICE_CONTAINER_VERSION)
        self.service_container_name = getenv(CONF_SERVICE_CONTAINER_NAME)

        self._properties = {
            'service_owner': getenv(CONF_SERVICE_OWNER),
            'service_name': getenv(CONF_SERVICE_NAME),
            'service_version': getenv(CONF_SERVICE_VERSION),
            'service_cluster': getenv(CONF_SERVICE_CLUSTER),
            'service_model_name': getenv(CONF_SERVICE_MODEL_NAME),
            'service_model_framework': getenv(CONF_SERVICE_MODEL_FRAMEWORK),
            'service_model_framework_version': getenv(CONF_SERVICE_MODEL_FRAMEOWRK_VERSION),
            'service_model_version': getenv(CONF_SERVICE_MODEL_VERSION),
            'service_container_version': getenv(CONF_SERVICE_CONTAINER_VERSION),
            'service_container_name': getenv(CONF_SERVICE_CONTAINER_NAME)
        }

    @property
    def properties(self):
        """The property context. This contains free-form properties that you can add to your telemetry.
        Returns:
            (dict). the context object.
        """
        return self._properties