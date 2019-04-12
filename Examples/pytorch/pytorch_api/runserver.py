# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from flask import Flask, request, abort
from flask_restful import Resource, Api
from ai4e_app_insights import AppInsights
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import APIService
from PIL import Image
import pytorch_classifier
from io import BytesIO
from os import getenv

print("Creating Application")

ACCEPTED_CONTENT_TYPES = ['image/png', 'application/octet-stream', 'image/jpeg']

app = Flask(__name__)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# Use the APIService to executes your functions within a logging trace, supports long-running/async functions,
# handles SIGTERM signals from AKS, etc., and handles concurrent requests.
with app.app_context():
    ai4e_service = APIService(app, log)

# Load the model
# The model was copied to this location when the container was built; see ../Dockerfile
model_path = '/app/pytorch_api/iNat_2018_InceptionV3.pth.tar'
model = pytorch_classifier.load_model(model_path)

# Define a function for processing request data, if appliciable.  This function loads data or files into
# a dictionary for access in your API function.  We pass this function as a parameter to your API setup.
def process_request_data(request):
    print('Processing data...')
    return_values = {'image_bytes': None}
    try:
        # Attempt to load the body
        return_values['image_bytes'] = BytesIO(request.data)
    except:
        log.log_error('Unable to load the request data')   # Log to Application Insights
    return return_values

# POST, async API endpoint example
@ai4e_service.api_sync_func(
    api_path = '/classify', 
    methods = ['POST'], 
    request_processing_function = process_request_data, # This is the data process function that you created above.
    maximum_concurrent_requests = 5, # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types = ACCEPTED_CONTENT_TYPES,
    content_max_length = 10000, # In bytes
    trace_name = 'post:classify')
def post(*args, **kwargs):
    print('Post called')
    image_bytes = kwargs.get('image_bytes')
    clss = pytorch_classifier.classify(model, image_bytes)
    # in this example we simply return the numerical ID of the most likely category determined
    # by the model
    return clss

if __name__ == '__main__':
    app.run()
