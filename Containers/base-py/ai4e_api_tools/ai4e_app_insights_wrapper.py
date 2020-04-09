# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# This libary is used to wrap many of the AzureLogHandler and metrics_exporter
# required objects into an easily usable package.

from os import getenv
import logging
from opencensus.ext.azure import metrics_exporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.stats import view as view_module
from opencensus.stats import stats as stats_module

APPINSIGHTS_INSTRUMENTATIONKEY = "APPINSIGHTS_INSTRUMENTATIONKEY"

stats = stats_module.stats
view_manager = stats.view_manager
stats_recorder = stats.stats_recorder

class AI4EAppInsights(object):
    def __init__(self):
        self.metrics = {}
        self.logger = logging.getLogger(__name__)

        self.appinsights_key = None
        raw_key = getenv(APPINSIGHTS_INSTRUMENTATIONKEY, None)
        if (raw_key and len(raw_key.strip()) > 0):
            self.appinsights_key = raw_key.strip()

        if (self.appinsights_key):
            handler = AzureLogHandler(connection_string='InstrumentationKey=' + str(getenv('APPINSIGHTS_INSTRUMENTATIONKEY')))
            self.logger.addHandler(handler)
            exporter = metrics_exporter.new_metrics_exporter(connection_string='InstrumentationKey=' + str(getenv('APPINSIGHTS_INSTRUMENTATIONKEY')))
            view_manager.register_exporter(exporter)

    def _log(self, message, sev, taskId = None, additionalProperties = None):
        if (taskId):
            if (additionalProperties is None):
                additionalProperties = { 'task_id': taskId }
            else:
                additionalProperties['task_id'] = taskId
        
        self.logger.log(sev, message, extra=additionalProperties)

    def log_debug(self, message, taskId = None, additionalProperties = None):
        self._log(message, 10, taskId, additionalProperties)

    def log_info(self, message, taskId = None, additionalProperties = None):
        self._log(message, 20, taskId, additionalProperties)

    def log_warn(self, message, taskId = None, additionalProperties = None):
        self._log(message, 30, taskId, additionalProperties)

    def log_error(self, message, taskId = None, additionalProperties = None):
        self._log(message, 40, taskId, additionalProperties)

    def log_exception(self, message, taskId = None, additionalProperties = None):
        self._log(message, 50, taskId, additionalProperties)

    def track_metric(self, metric_name, metric_value):
        if (self.appinsights_key):
            print("Tracking metric:" + metric_name + ", Value: " + str(metric_value))

            if (not metric_name in self.metrics):
                metrics_measure = measure_module.MeasureInt(metric_name, metric_name, metric_name)
                metrics_view = view_module.View(metric_name, metric_name, [], metrics_measure, aggregation_module.LastValueAggregation(value=metric_value))

                view_manager.register_view(metrics_view)
                mmap = stats_recorder.new_measurement_map()
                tmap = tag_map_module.TagMap()

                self.metrics[metric_name] = {'measure': metrics_measure, 'measurement_map': mmap, 'tag_map': tmap}

            measure = self.metrics[metric_name]['measure']
            mmap = self.metrics[metric_name]['measurement_map']
            tmap = self.metrics[metric_name]['tag_map']
            print("Putting metric:" + metric_name + ", Value: " + str(metric_value))
            mmap.measure_int_put(measure, metric_value)
            mmap.record(tmap)