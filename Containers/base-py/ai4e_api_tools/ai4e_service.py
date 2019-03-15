# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from threading import Thread
from os import getenv
from opencensus.trace.ext.flask.flask_middleware import FlaskMiddleware
from opencensus.trace.tracer import Tracer
from opencensus.trace.exporters.ocagent import trace_exporter
from opencensus.trace.exporters.transports.background_thread import BackgroundThreadTransport
from flask import Flask, abort, request, current_app
from flask_restful import Resource, Api
import signal
from ai4e_app_insights import AppInsights
from task_management.api_task import ApiTaskManager
import sys
from functools import wraps

# Use OpenCensus to send traces to Application Insights
export_LocalForwarder = trace_exporter.TraceExporter(
    transport=BackgroundThreadTransport,
    service_name=getenv("SERVICE_OWNER", "Default") + ":" + getenv("SERVICE_MODEL_NAME", "Default"),
    endpoint=getenv('OCAGENT_TRACE_EXPORTER_ENDPOINT'))
tracer = Tracer(exporter=export_LocalForwarder)

MAX_REQUESTS_KEY_NAME = 'max_requests'
CONTENT_TYPE_KEY_NAME = 'content_type'
CONTENT_MAX_KEY_NAME = 'content_max_length'

class AI4EService():
    def __init__(self, flask_app, logger):
        self.app = flask_app
        self.log = logger
        self.api = Api(self.app)
        self.appinsights = AppInsights(self.app)
        self.is_terminating = False
        self.func_properties = {}
        self.func_request_counts = {}
        self.api_prefix = getenv('API_PREFIX')
        
        self.api_task_manager = ApiTaskManager(flask_api=self.api, resource_prefix=self.api_prefix)
        signal.signal(signal.SIGINT, self.initialize_term)

        self.app.add_url_rule('/', view_func = self.health_check, methods=['GET'])
        self.app.before_request(self.before_request)

    def health_check(self):
        return 'Health check OK'
    
    def api_func(self, is_async, api_path, methods, request_processing_function, maximum_concurrent_requests, content_type = None, content_max_length = None, trace_name = None, *args, **kwargs):
        def decorator_api_func(func):
            if not api_path in self.func_properties:
                self.func_properties[api_path] = {MAX_REQUESTS_KEY_NAME: maximum_concurrent_requests, CONTENT_TYPE_KEY_NAME: content_type, CONTENT_MAX_KEY_NAME: content_max_length}
                self.func_request_counts[api_path] = 0

            @wraps(func)
            def api(*args, **kwargs):
                internal_args = {"func": func, "api_path": api_path}

                if request_processing_function:
                    return_values = request_processing_function(request)
                    combined_kwargs = {**internal_args, **kwargs, **return_values}
                else:
                    combined_kwargs = {**internal_args, **kwargs}
                
                if is_async:
                    task_info = self.api_task_manager.AddTask(request)
                    taskId = str(task_info['uuid'])
                    combined_kwargs["taskId"] = taskId

                    self.wrap_async_endpoint(trace_name, *args, **combined_kwargs)
                    return 'TaskId: ' + taskId
                else:
                    return self.wrap_sync_endpoint(trace_name, *args, **combined_kwargs)

            api.__name__ = 'api_' + api_path.replace('/', '')
            print("Adding url rule: " + self.api_prefix + api_path + ", " + api.__name__)
            self.app.add_url_rule(self.api_prefix + api_path, view_func = api, methods=methods, provide_automatic_options=True)
        return decorator_api_func

    def api_async_func(self, api_path, methods, request_processing_function = None, maximum_concurrent_requests = None, content_type = None, content_max_length = None, trace_name = None, *args, **kwargs):
        is_async = True
        return self.api_func(is_async, api_path, methods, request_processing_function, maximum_concurrent_requests, content_type = None, content_max_length = None, trace_name = None, *args, **kwargs)

    def api_sync_func(self, api_path, methods, request_processing_function = None, maximum_concurrent_requests = None, content_type = None, content_max_length = None, trace_name=None, *args, **kwargs):
        is_async = False
        return self.api_func(is_async, api_path, methods, request_processing_function, maximum_concurrent_requests, content_type = None, content_max_length = None, trace_name = None, *args, **kwargs)

    def initialize_term(signum, frame):
        print('Signal handler called with signal: ' + signum)
        print('SIGINT received, service is terminating and will no longer accept requests.')
        self.is_terminating = True

    def before_request(self):
        # Don't accept a request if SIGTERM has been called on this instance.
        if (self.is_terminating):
            abort(503, {'message': 'Service is busy, please try again later.'})

        if request.path in self.func_properties:
            if (self.func_request_counts[request.path] + 1 > self.func_properties[request.path][MAX_REQUESTS_KEY_NAME]):
                abort(503, {'message': 'Service is busy, please try again later.'})

            if (self.func_properties[request.path][CONTENT_TYPE_KEY_NAME] and not request.content_type == self.func_properties[request.path][CONTENT_TYPE_KEY_NAME]):
                abort(401, {'message': 'Content-type must be ' + self.func_properties[request.path][CONTENT_TYPE_KEY_NAME]})

            if (self.func_properties[request.path][CONTENT_MAX_KEY_NAME] and request.content_length > self.func_properties[request.path][CONTENT_MAX_KEY_NAME]):
                abort(413, {'message': 'Request content too large (' + str(request.content_length) + "). Must be smaller than: " + str(self.func_properties[request.path][CONTENT_MAX_KEY_NAME])})

    def increment_requests(self, api_path):
        self.func_request_counts[api_path] += 1

    def decrement_requests(self, api_path):
        self.func_request_counts[api_path] -= 1

    def wrap_sync_endpoint(self, trace_name=None, *args, **kwargs):
        if (trace_name):
            with tracer.span(name=trace_name) as span:
                return self._execute_func_with_counter(*args, **kwargs)
        else:
            return self._execute_func_with_counter(*args, **kwargs)

    def wrap_async_endpoint(self, trace_name=None, *args, **kwargs):
        if (trace_name):
            with tracer.span(name=trace_name) as span:
                self._create_and_execute_thread(*args, **kwargs)
        else:
            self._create_and_execute_thread(*args, **kwargs)

    def _create_and_execute_thread(self, *args, **kwargs):
        kwargs['request'] = request
        thread = Thread(target = self._execute_func_with_counter, args=args, kwargs=kwargs)
        thread.start()

    def _execute_func_with_counter(self, *args, **kwargs):
        func = kwargs['func']
        api_path = kwargs['api_path']

        self.increment_requests(api_path)
        try:
            r = func(*args, **kwargs)
            return r
        except:
            taskId = kwargs['taskId']
            if taskId:
                self.log.log_exception(sys.exc_info()[0], taskId)
                self.api_task_manager.FailTask(taskId, 'Task failed - try again')
            else:
                self.log.log_exception(sys.exc_info()[0])
            abort(500)
        finally:
            self.decrement_requests(api_path)