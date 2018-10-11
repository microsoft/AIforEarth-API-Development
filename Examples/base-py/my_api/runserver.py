# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# # /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from task_management.api_task import ApiTaskManager
from flask import Flask, request
from flask_restful import Resource, Api
from time import sleep
import json
from ai4e_app_insights import AppInsights
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import AI4EWrapper
import sys
from os import getenv

print("Creating Application")

api_prefix = getenv('API_PREFIX')
app = Flask(__name__)
api = Api(app)

# Log requests, traces and exceptions to the Application Insights service
appinsights = AppInsights(app)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the internal-container AI for Earth Task Manager (not for production use!).
api_task_manager = ApiTaskManager(flask_api=api, resource_prefix=api_prefix)

ai4e_wrapper = AI4EWrapper(app)

# POST, long-running/async API endpoint example
@app.route(api_prefix + '/', methods=['POST'])
def post():
    # The AddTask function returns a dictonary of task information:
    #   - uuid: taskId used to update/retrieve task status
    #   - status: string that was passed via the AddTask or UpdateTaskStatus function
    #   - timestamp
    #   - endpoint: passed via the ApiTaskManager constructor

    # Add a task and extract its id, so the caller can keep track of it.
    task_info = api_task_manager.AddTask('queued')
    taskId = str(task_info["uuid"])

    try:
        post_body = json.loads(request.data)
    except:
        return "Unable to parse the request body. Please request with valid json."

    # wrap_async_endpoint executes your function in a new thread and wraps it within a logging trace. 
    ai4e_wrapper.wrap_async_endpoint(my_long_running_funct, "post:my_long_running_funct", taskId = taskId, json_body = post_body)

    # Always return the taskId to the caller.
    return 'TaskId: ' + taskId

# GET, sync API endpoint example
@app.route(api_prefix + '/echo/<string:text>', methods=['GET'])
def echo(text):
    # wrap_sync_endpoint wraps your function within a logging trace.
    return ai4e_wrapper.wrap_sync_endpoint(my_sync_function, "post:my_long_running_funct", echo_text=text)

def my_long_running_funct(**kwargs):
    taskId = kwargs.get('taskId', None)
    # Update the task status, so the caller knows it has been accepted and is running.
    api_task_manager.UpdateTaskStatus(taskId, 'running')

    json_body = kwargs.get('json_body', None)
    if (not json_body):
        # Log errors and make sure the status is updated.
        log.log_error("Body is missing", taskId)
        api_task_manager.UpdateTaskStatus(taskId, 'failed - Body is required')
        return -1

    try:
        #INSERT_YOUR_MODEL_CALL_HERE
        sleep(10)  # replace with real code
    except:
        log.log_exception(sys.exc_info()[0], taskId)

    # Once complete, ensure the status is updated.
    log.log_debug("Completed task", taskId)
    api_task_manager.UpdateTaskStatus(taskId, 'completed')

def my_sync_function(**kwargs):
    echo_text = kwargs.get('echo_text', '')
    return 'Echo: ' + echo_text

if __name__ == '__main__':
    app.run()