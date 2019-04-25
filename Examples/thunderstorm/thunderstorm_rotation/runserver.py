# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# # /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from time import sleep
import json
from flask import Flask, request, abort
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService
from os import getenv

import numpy
import utils
from sklearn.externals import joblib
import sklearn.linear_model
import io
from sas_blob import SasBlob

print('Creating Application')

app = Flask(__name__)

# Use the AI4EAppInsights library to send log messages. NOT REQURIED
log = AI4EAppInsights()

# Use the APIService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = APIService(app, log)

def load_model():
    return joblib.load(getenv('MODEL_PATH'))

linreg_model = load_model()
sas_blob_helper = SasBlob()

# Define a function for processing request data, if appliciable.  This function loads data or files into
# a dictionary for access in your API function.  We pass this function as a parameter to your API setup.
def process_request_data_sync(request):
    return_values = {'predictor_table': None}
    try:
        files, names = [], []
        for name, file in request.files.items():
            print(file.content_type)
            files.append(file)
            names.append(name)
            
        (metadata_table, predictor_table, target_table) = utils.read_many_feature_files(files)

        return_values['predictor_table'] = predictor_table
    except Exception as e:
        print(e)
        log.log_error('Unable to load the request data')   # Log to Application Insights
        abort('Unable to load the request data' + str(e))
    return return_values

def process_request_data_async(request):
    return_values = {'predictor_table': None, 'output_sas_url': None}
    try:
        if not request.data:
            log.log_error('JSON body is required')   # Log to Application Insights
            abort('JSON body is required')

        json_body = json.loads(request.data)

        if 'track_step_file_names' not in json_body or 'sas_container' not in json_body:
            log.log_error('track_step_file_names and sas_container are required in the JSON body')   # Log to Application Insights
            abort('track_step_file_names and sas_container are required in the JSON body')

        container_uri = json_body['sas_container']
        return_values['output_sas_url'] = container_uri

        file_contents = []
        for track_step_file_name in json_body['track_step_file_names']:
            print("Found " + track_step_file_name)
            file_contents.append(sas_blob_helper.get_blob_sas_uri(container_uri, track_step_file_name))

        (metadata_table, predictor_table, target_table) = utils.read_many_feature_files(file_contents)

        return_values['predictor_table'] = predictor_table
    except Exception as e:
        print(e)
        log.log_error('Unable to load the request data')   # Log to Application Insights
        abort('Unable to load the request data' + e)
    return return_values

def predict_from_model(predictor_table, taskId = None):
    if taskId:
        ai4e_service.api_task_manager.UpdateTaskStatus(taskId, 'running model')

    training_predictions = linreg_model.predict(predictor_table.as_matrix())
    return training_predictions

# POST, long-running/async API endpoint example
@ai4e_service.api_async_func(
    api_path = '/predict', 
    methods = ['POST'], 
    request_processing_function = process_request_data_async, # This is the data process function that you created above.
    maximum_concurrent_requests = 5, # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types = ['application/json', 'application/octet-stream'],
    content_max_length = 1024 * 1024, # In bytes
    trace_name = 'predict')
def predict_long(*args, **kwargs):
    # Since this is an async function, we need to keep the task updated.
    taskId = kwargs.get('taskId')
    log.log_debug('Started task', taskId) # Log to Application Insights

    # Get the data from the dictionary key that you assigned in your process_request_data function.
    predictor_table = kwargs.get('predictor_table')
    output_sas_url = kwargs.get('output_sas_url')

    # Run your model function
    training_predictions = predict_from_model(predictor_table)
    output = io.StringIO()
    numpy.savetxt(output, training_predictions)
    output_uri = sas_blob_helper.write_blob_from_text(output_sas_url, 'prediction.csv', output.getvalue())

    # Once complete, ensure the status is updated.
    log.log_debug('Completed task', taskId) # Log to Application Insights
    # Update the task with a completion event.
    ai4e_service.api_task_manager.CompleteTask(taskId, 'completed - output written to ' + output_uri)

# GET, sync API endpoint example
@ai4e_service.api_sync_func(
    api_path = '/predict_short', 
    methods = ['POST'],
    request_processing_function = process_request_data_sync,
    maximum_concurrent_requests = 100, 
    content_types = ['application/octet-stream'],
    trace_name = 'predict_short')
def predict_short(*args, **kwargs):
    predictor_table = kwargs.get('predictor_table')
    try:
        training_predictions = predict_from_model(predictor_table)
        output = io.StringIO()
        numpy.savetxt(output, training_predictions)
        return output.getvalue()
    except Exception as e:
        print(e)
    return training_predictions
if __name__ == '__main__':
    app.run()