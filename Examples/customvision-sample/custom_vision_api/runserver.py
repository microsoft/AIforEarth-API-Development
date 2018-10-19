# /ai4e_api_tools has been added to the PYTHONPATH, so we can reference those
# libraries directly.
from flask import Flask, request
from flask_restful import Resource, Api
import json
from ai4e_app_insights import AppInsights
from ai4e_app_insights_wrapper import AI4EAppInsights
from ai4e_service import AI4EWrapper
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

api_prefix = getenv('API_PREFIX')
app = Flask(__name__)
api = Api(app)
print(api_prefix)

# Log requests, traces and exceptions to the Application Insights service
appinsights = AppInsights(app)

# Use the AI4EAppInsights library to send log messages.
log = AI4EAppInsights()

# The API4EWrapper instruments your functions so that trace metrics are logged.
ai4e_wrapper = AI4EWrapper(app)

# Healthcheck endpoint - this lets us quickly retrieve the status of your API.
@app.route('/', methods=['GET'])
def health_check():
    return "Health check OK"

# POST, sync API endpoint example
@app.route(api_prefix + '/', methods=['POST'])
def post():
    try:
        post_body = json.loads(request.data)
    except:
        return "Unable to parse the request body. Please request with valid json."

    # wrap_sync_endpoint wraps your function within a logging trace.
    return ai4e_wrapper.wrap_sync_endpoint(predict_image, "post:predict_image", json_body = post_body)

def predict_image(**kwargs):
    json_body = kwargs.get('json_body', None)
    if (not json_body):
        log.log_error("Body is missing")
        return -1

    if (not "img_url" in json_body):
        log.log_error("img_url is required as input.")
        return -1

    try:
        # Extract the img_url input from the json body
        test_img_url = json_body["img_url"]

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