# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from task_management.api_task import ApiTaskManager
from flask import Flask, request, send_file, abort
from flask_restful import Resource, Api
from ai4e_app_insights import AppInsights
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import AI4EWrapper
from sas_blob import SasBlob
from PIL import Image
import tf_detector
from io import BytesIO
from os import getenv
import uuid
import sys

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ['image/png', 'application/octet-stream', 'image/jpeg']
blob_access_duration_hrs = 1

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

# Load the model
# The model was copied to this location when the container was built; see ../Dockerfile
model_path = '/app/tf_iNat_api/frozen_inference_graph.pb'
detection_graph = tf_detector.load_model(model_path)

# Healthcheck endpoint - this lets us quickly retrieve the status of your API.
@app.route('/', methods=['GET'])
def health_check():
    return "Health check OK"

# POST, sync API endpoint example
@app.route(api_prefix + '/detect', methods=['POST'])
def post():
    if not request.headers.get("Content-Type") in ACCEPTED_CONTENT_TYPES:
        return abort(415, "Unable to process request. Only png or jpeg files are accepted as input")

    # Add a task and extract its id, so the caller can keep track of it.
    task_info = api_task_manager.AddTask('queued')
    taskId = str(task_info["uuid"])

    image_bytes = BytesIO(request.data)

    # wrap_async_endpoint executes your function in a new thread and wraps it within a logging trace. 
    ai4e_wrapper.wrap_async_endpoint(detect, "post:detect", taskId = taskId, image=image_bytes)

    # Always return the taskId to the caller.
    return 'TaskId: ' + taskId

def detect(**kwargs):
    print('runserver.py: detect() called, generating detections...')
    taskId = kwargs.get('taskId', None)
    image = kwargs.get('image', None)

    # Update the task status, so the caller knows it has been accepted and is running.
    api_task_manager.UpdateTaskStatus(taskId, 'running - generate_detections')

    try:
        boxes, scores, clsses, image = tf_detector.generate_detections(
            detection_graph, image)

        api_task_manager.UpdateTaskStatus(taskId, 'rendering boxes')
        print('runserver.py: detections generated, rendering boxes...')
        # image is modified in place
        # here confidence_threshold is hardcoded, but you can ask that as a input from the request
        tf_detector.render_bounding_boxes(
            boxes, scores, clsses, image, confidence_threshold=0.5)

        image.seek(0)

        sas_blob_helper = SasBlob()
        # Create a unique name for a blob container
        container_name = str(uuid.uuid4()).replace('-','')

        # Create a writable sas container and return its url
        sas_url = sas_blob_helper.create_writable_container_sas(getenv('STORAGE_ACCOUNT_NAME'), getenv('STORAGE_ACCOUNT_KEY'), container_name, blob_access_duration_hrs)

        # Write the image to the blob
        sas_blob_helper.write_blob(sas_url, 'detect_output.jpg', image)
        
        api_task_manager.UpdateTaskStatus(taskId, 'completed - output written to: ' + sas_url)
    except:
        log.log_exception(sys.exc_info()[0], taskId)
        api_task_manager.UpdateTaskStatus(taskId, 'failed: ' + str(sys.exc_info()[0]))

# GET, sync API endpoint example
@app.route(api_prefix + '/echo/<string:text>', methods=['GET'])
def echo(text):
    # wrap_sync_endpoint wraps your function within a logging trace.
    return ai4e_wrapper.wrap_sync_endpoint(my_sync_function, "post:my_long_running_funct", echo_text=text)

def my_sync_function(**kwargs):
    echo_text = kwargs.get('echo_text', '')
    return 'Echo: ' + echo_text

if __name__ == '__main__':
    app.run()