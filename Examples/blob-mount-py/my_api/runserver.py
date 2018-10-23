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
import os
from os import getenv

print("Creating Application")

api_prefix = getenv('API_PREFIX')
app = Flask(__name__)
api = Api(app)
blob_mapped_dir = "/mnt/input"

# Log requests, traces and exceptions to the Application Insights service
appinsights = AppInsights(app)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the internal-container AI for Earth Task Manager (not for production use!).
api_task_manager = ApiTaskManager(flask_api=api, resource_prefix=api_prefix)

# Use the AI4EWrapper to executes your functions within a logging trace.
# Also, helps support long-running/async functions.
ai4e_wrapper = AI4EWrapper(app)

def read_blob_file(filename):
    data_path = os.path.join(blob_mapped_dir, filename)
    with open(data_path, "r") as file_from_blob:
        return file_from_blob.read()

@app.route('/', methods=['GET'])
def health_check():
    return "Health check OK"

# POST, long-running/async API endpoint example
@app.route(api_prefix + '/', methods=['POST'])
def post():
    # The AddTask function returns a dictonary of task information:
    #   - uuid: taskId used to update/retrieve task status
    #   - status: string that was passed via the AddTask or UpdateTaskStatus function
    #   - timestamp
    #   - endpoint: passed via the ApiTaskManager constructor

    try:
        filename = "config.csv"
        #INSERT_YOUR_MODEL_CALL_HERE
        ai4e_wrapper.wrap_sync_endpoint(read_blob_file, "post:read_blob_file", filename = filename)
        return "Blob file contents: " + read_blob_file(filename)
    except:
        return "Unable to parse the request body. Please request with valid json."

# GET, sync API endpoint example
@app.route(api_prefix + '/echo/<string:text>', methods=['GET'])
def echo(text):
    # wrap_sync_endpoint wraps your function within a logging trace.
    return ai4e_wrapper.wrap_sync_endpoint(my_sync_function, "post:echo", echo_text=text)

def my_sync_function(**kwargs):
    echo_text = kwargs.get('echo_text', '')
    return 'Echo: ' + echo_text

if __name__ == '__main__':
    app.run()