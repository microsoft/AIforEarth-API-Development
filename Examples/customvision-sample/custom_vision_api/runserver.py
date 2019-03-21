# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from flask import Flask, request
import json
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import AI4EService
import sys
from os import getenv

# These are specific to Custom Vision.  
from azure.cognitiveservices.vision.customvision.prediction import prediction_endpoint
from azure.cognitiveservices.vision.customvision.prediction.prediction_endpoint import models

# Replace these variables with your own Custom Vision values.
prediction_key = getenv('CUSTOM_VISION_PREDICTION_KEY')  
iteration_id = getenv('CUSTOM_VISION_ITERATION_ID')
project_id = getenv('CUSTOM_VISION_PROJECT_ID')

print("Creating Application")

app = Flask(__name__)

# Define a function for processing request data, if appliciable.  This function loads data or files into
# a dictionary for access in your API function.  We pass this function as a parameter to your API setup.
def process_request_data(request):
    return_values = {'post_body': None}
    try:
        # Attempt to load the body
        return_values['post_body'] = json.loads(request.data)
    except:
        log.log_error('Unable to load the request data')   # Log to Application Insights
    return return_values

# POST, sync API endpoint example
@ai4e_service.api_sync_func(
    api_path = '/', 
    methods = ['POST'], 
    request_processing_function = process_request_data, # This is the data process function that you created above.
    maximum_concurrent_requests = 5, # If the number of requests exceed this limit, a 503 is returned to the caller.
    content_types = ['application/json'],
    content_max_length = 10000, # In bytes
    trace_name = 'post:predict_image')
def post():
    post_json = kwargs.get('post_body')
    
    if (not "img_url" in post_json):
        log.log_error("img_url is required as input.")
        return -1

    try:
        # Extract the img_url input from the json body
        test_img_url = post_json["img_url"]

        # Here's how to debug
        print(test_img_url)         # You can check this in Postman 
        log.log_debug(test_img_url) # You can check this in Application Insights

        # Call the Custom Vision service endpoint
        predictor = prediction_endpoint.PredictionEndpoint(prediction_key)
        results = predictor.predict_image_url(project_id, iteration_id, url=test_img_url)

        # Construct the predictions for output
        ret = []
        for prediction in results.predictions:
            pred = {}
            pred['prediction'] = prediction.tag_name
            pred['confidence'] = "{0:.2f}%".format(prediction.probability * 100)
            ret.append(pred.copy())
            
        # Format and return output
        return json.dumps(ret)
    except:
        print(sys.exc_info()[0])
        log.log_exception(sys.exc_info()[0])

if __name__ == '__main__':
    app.run()