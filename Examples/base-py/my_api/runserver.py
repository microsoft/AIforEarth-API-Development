# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# # /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from time import sleep
import json
from flask import Flask, request, abort
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import AI4EService
from os import getenv

print('Creating Application')

app = Flask(__name__)

# Use the AI4EAppInsights library to send log messages. NOT REQURIED
log = AI4EAppInsights()

# Use the AI4EService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = AI4EService(app, log)

# Define a function for processing request data, if appliciable.  This function loads data or files into
# a dictionary for access in your API function.  We pass this function as a parameter to your API setup.
def process_request_data(request):
    return_values = {'data': None}
    try:
        # Attempt to load the body
        return_values['data'] = request.data
    except:
        log.log_error('Unable to load the request data')   # Log to Application Insights
    return return_values

# Define a function that runs your model.  This could be in a library.
def run_model(taskId, body):
    # Update the task status, so the caller knows it has been accepted and is running.
    ai4e_service.api_task_manager.UpdateTaskStatus(taskId, 'running model')

    log.log_debug('Running model', taskId) # Log to Application Insights
    #INSERT_YOUR_MODEL_CALL_HERE
    sleep(10)  # replace with real code

# POST, long-running/async API endpoint example
@ai4e_service.api_async_func(
    api_path = '/', 
    methods = ['POST'], 
    request_processing_function = process_request_data, # This is the data process function that you created above.
    maximum_concurrent_requests = 5, # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types = ['application/json'],
    content_max_length = 1000, # In bytes
    trace_name = 'post:my_long_running_funct')
def default_post(*args, **kwargs):
    # Since this is an async function, we need to keep the task updated.
    taskId = kwargs.get('taskId')
    log.log_debug('Started task', taskId) # Log to Application Insights

    # Get the data from the dictionary key that you assigned in your process_request_data function.
    request_data = kwargs.get('data')

    if not request_data:
        ai4e_service.api_task_manager.FailTask(taskId, 'Task failed - Body was empty or could not be parsed.')
        return -1

    # Load the request data into JSON format.
    request_json = json.loads(request_data)

    # Run your model function
    run_model(taskId, request_json)

    # Once complete, ensure the status is updated.
    log.log_debug('Completed task', taskId) # Log to Application Insights
    # Update the task with a completion event.
    ai4e_service.api_task_manager.CompleteTask(taskId, 'completed')

# GET, sync API endpoint example
@ai4e_service.api_sync_func(api_path = '/echo/<string:text>', methods = ['GET'], maximum_concurrent_requests = 1000, trace_name = 'post:echo', kwargs = {'text'})
def echo(*args, **kwargs):
    return 'Echo: ' + kwargs['text']

if __name__ == '__main__':
    app.run()