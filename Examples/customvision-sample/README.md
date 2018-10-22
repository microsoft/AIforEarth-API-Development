# Custom Vision API Example
This example is for hosting a Custom Vision model on the AI for Earth infrastructure.  It assumes that you have an existing Custom Vision project.  To get started building your first Custom Vision model, please see [here](https://docs.microsoft.com/en-us/azure/cognitive-services/custom-vision-service/getting-started-build-a-classifier).  

## Usage instructions
1. You will need to update the service_settings.env file with your specific Custom Vision project settings.  There are three Custom-Vision-specific settings:
+ CUSTOM_VISION_PREDICTION_KEY
+ CUSTOM_VISION_PROJECT_ID
+ CUSTOM_VISION_ITERATION_ID

To obtain these, navigate to the [Custom Vision site](https://customvision.ai/), sign in, and click on the project that you want to host.  Then, click on the gear icon in the upper right.  

![Custom Vision Settings](..\screenshots\CustomVisionSettings.jpg)

2. In the Project Settings section, copy the value from the Project Id field.  In the Accounts section, copy the value from the Prediction Key field.  Update the service_settings.env file with both of these values.   
3. Then on the Custom Vision site, click on the "Performance" tab on the top menu bar.  In the left sidebar, click on the iteration of your  model that you want to use.  (NOTE: you will not see iterations until after you have trained a model.)  Then click on the "Prediction URL" button near the top.  

![Custom Vision Iteration ID](..\screenshots\CustomVisionIterationID.jpg)

4. Scroll to the end of either of the Prediction URLs, and you will find the iteration ID.  Update the final Custom Vision setting in service_settings.env with this value.  

Please ensure that you also change your inputs and outputs in the custom_vision_api\runserver.py file, update your Application Insights values for logging, and all of the other work items documented in the Quickstart.  

