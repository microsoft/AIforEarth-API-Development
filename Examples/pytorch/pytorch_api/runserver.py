# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from task_management.api_task import ApiTaskManager
from flask import Flask, request, send_file, abort
from flask_restful import Resource, Api
from ai4e_app_insights import AppInsights
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import AI4EWrapper
from PIL import Image
import pytorch_classifier
from io import BytesIO
from os import getenv

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ['image/png', 'application/octet-stream']

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
model_path = '/app/pytorch_api/iNat_2018_InceptionV3.pth.tar'
model = pytorch_classifier.load_model(model_path)

# Healthcheck endpoint - this lets us quickly retrieve the status of your API.
@app.route('/', methods=['GET'])
def health_check():
    return "Health check OK"

# POST, sync API endpoint example
@app.route(api_prefix + '/classify', methods=['POST'])
def post():
    if not request.headers.get("Content-Type") in ACCEPTED_CONTENT_TYPES:
        return abort(415, "Unable to process request. Only png files are accepted as input")

    try:
        image = BytesIO(request.data)
    except:
        return 'Unable to open the image.'
    return ai4e_wrapper.wrap_sync_endpoint(classify, "post:detect", image_bytes=image)

def classify(**kwargs):
    print('runserver.py: classify() called...')
    image_bytes = kwargs.get('image_bytes', None)

    clss = pytorch_classifier.classify(model, image_bytes)

    # in this example we simply return the numerical ID of the most likely category determined
    # by the model
    return clss


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
