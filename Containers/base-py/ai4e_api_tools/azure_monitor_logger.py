import logging
from os import getenv
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.stats import aggregation as aggregation_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.ext.azure import metrics_exporter
from opencensus.stats import measure as measure_module
from opencensus.stats import view as view_module
from opencensus.trace.samplers import ProbabilitySampler, AlwaysOnSampler
from opencensus.trace.tracer import Tracer
from opencensus.stats import stats as stats_module
from opencensus.trace import config_integration

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

class AzureMonitorLogger(object):
    def __init__(self, logger, flask_app=None):
        self._properties = {
            'service_name': getenv(CONF_SERVICE_NAME),
            'service_version': getenv(CONF_SERVICE_VERSION),
            'service_cluster': getenv(CONF_SERVICE_CLUSTER),
            'service_model_name': getenv(CONF_SERVICE_MODEL_NAME),
            'service_model_version': getenv(CONF_SERVICE_MODEL_VERSION),
            'service_container_version': getenv(CONF_SERVICE_CONTAINER_VERSION),
            'service_container_name': getenv(CONF_SERVICE_CONTAINER_NAME),
            'task_id': 'none'
        }
        self.logger = logger
        self.metrics = {}
        self.tracer = None
        self.appinsights_key = getenv('APPINSIGHTS_INSTRUMENTATIONKEY', None)

        if self.appinsights_key:
            try:
                print('Setting up Azure Monitor with Application Insights.')
                config_integration.trace_integrations(['logging'])
                #self.logger = logging.getLogger(getenv(CONF_SERVICE_NAME))
                self.logger.setLevel(logging.INFO)
                handler = AzureLogHandler(connection_string='InstrumentationKey=' + self.appinsights_key)
                self.logger.addHandler(handler)

                self.azure_exporter=AzureExporter(connection_string='InstrumentationKey=' + self.appinsights_key, timeout=getenv('APPINSIGHTS_TIMEOUT', 30.0))            

                sampling_rate = getenv('TRACE_SAMPLING_RATE', None)
                if not sampling_rate:
                    sampling_rate = 1.0
                
                self.middleware = None
                if flask_app:
                    self.middleware = FlaskMiddleware(
                        flask_app,
                        exporter=self.azure_exporter,
                        sampler=ProbabilitySampler(rate=float(sampling_rate)),
                    )

                #self.tracer = Tracer(
                #    exporter=self.azure_exporter,
                #    sampler=ProbabilitySampler(rate=float(sampling_rate)),
                #)
                self.tracer = Tracer(exporter=self.azure_exporter, sampler=AlwaysOnSampler())

                self.metrics_exporter = metrics_exporter.new_metrics_exporter(connection_string='InstrumentationKey=' + self.appinsights_key)
                stats = stats_module.stats
                self.view_manager = stats.view_manager
                self.view_manager.register_exporter(self.metrics_exporter)
                self.stats_recorder = stats.stats_recorder
            except Exception as e:
                print('Exception in setting up the Azure Monitor:')
                print(e)

    def log_debug(self, message, taskId = None, additionalProperties = None):
        properties = self._properties
        properties['task_id'] = taskId
        if additionalProperties:
            properties.update(additionalProperties)

        custom_dimensions = {'custom_dimensions': properties}
        self.logger.debug(message, extra=custom_dimensions)

    def log_info(self, message, taskId = None, additionalProperties = None):
        properties = self._properties
        properties['task_id'] = taskId
        if additionalProperties:
            properties.update(additionalProperties)
        
        custom_dimensions = {'custom_dimensions': properties}

        self.logger.info(message, extra=custom_dimensions)

    def log_warn(self, message, taskId = None, additionalProperties = None):
        properties = self._properties
        properties['task_id'] = taskId
        if additionalProperties:
            properties.update(additionalProperties)

        custom_dimensions = {'custom_dimensions': properties}
        self.logger.warning(message, extra=custom_dimensions)

    def log_error(self, message, taskId = None, additionalProperties = None):
        properties = self._properties
        properties['task_id'] = taskId
        if additionalProperties:
            properties.update(additionalProperties)

        custom_dimensions = {'custom_dimensions': properties}
        self.logger.error(message, extra=custom_dimensions)

    def log_exception(self, message, taskId = None, additionalProperties = None):
        properties = self._properties
        properties['task_id'] = taskId
        if additionalProperties:
            properties.update(additionalProperties)

        custom_dimensions = {'custom_dimensions': properties}
        self.logger.exception(message, extra=custom_dimensions)

    def track_metric(self, metric_name, metric_value):
        try:
            if (self.appinsights_key):
                if (not metric_name in self.metrics):
                    metrics_measure = measure_module.MeasureInt(metric_name, metric_name, metric_name)
                    metrics_view = view_module.View(metric_name, metric_name, [], metrics_measure, aggregation_module.LastValueAggregation(value=metric_value))

                    self.view_manager.register_view(metrics_view)
                    mmap = self.stats_recorder.new_measurement_map()
                    tmap = tag_map_module.TagMap()

                    self.metrics[metric_name] = {'measure': metrics_measure, 'measurement_map': mmap, 'tag_map': tmap}

                measure = self.metrics[metric_name]['measure']
                mmap = self.metrics[metric_name]['measurement_map']
                tmap = self.metrics[metric_name]['tag_map']
                mmap.measure_int_put(measure, metric_value)
                mmap.record(tmap)
        except Exception as e:
            print('Exception when tracking a metric:')
            print(e)
