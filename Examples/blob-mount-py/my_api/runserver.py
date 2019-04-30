# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# # /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from flask import Flask, request
from time import sleep
import json
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService
import sys
import os
from os import getenv

print("Creating Application")

app = Flask(__name__)
blob_mapped_dir = "/mnt/input"

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the APIService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = APIService(app, log)

# Define a function for processing request data, if appliciable.  This function loads data or files into
# a dictionary for access in your API function.  We pass this function as a parameter to your API setup.
def process_request_data(request):
    return_values = {'image_bytes': None}
    try:
        # Attempt to load the body
        return_values['image_bytes'] = BytesIO(request.data)
    except:
        log.log_error('Unable to load the request data')   # Log to Application Insights
    return return_values

# POST, long-running/async API endpoint example
@ai4e_service.api_sync_func(
    api_path = '/example', 
    methods = ['POST'], 
    maximum_concurrent_requests = 10, # If the number of requests exceed this limit, a 503 is returned to the caller.
    trace_name = 'post:read_blob_file')
def post(*args, **kwargs):
    # The AddTask function returns a dictonary of task information:
    #   - uuid: taskId used to update/retrieve task status
    #   - status: string that was passed via the AddTask or UpdateTaskStatus function
    #   - timestamp
    #   - endpoint: passed via the TaskManager constructor

    filename = "config.csv"
    data_path = os.path.join(blob_mapped_dir, filename)
    with open(data_path, "r") as file_from_blob:
        return "Blob file contents: " + file_from_blob.read()

if __name__ == '__main__':
    app.run()