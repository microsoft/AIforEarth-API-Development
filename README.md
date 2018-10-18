# AI for Earth - Creating APIs
These images and examples are meant to illustrate how to build containers for use in the AI for Earth API system.

## Contents
1. [Repo Layout](#repo-layout)
2. [Quickstart](#Quickstart)
    1. [Choose a base image or example](#Choose-a-base-image-or-example)
    2. [Insert code to call your model](#Insert-code-to-call-your-model)
    3. [Input handling](#Input-handling)
    4. [Output handling](#Output-handling)
    5. [Create AppInsights instrumentation keys (optional)](#Create-AppInsights-instrumentation-keys)
    6. [Install required packages](#Install-required-packages)
    7. [Set environment variables](#Set-environment-variables)
    8. [Build and run your image](#Build-and-run-your-image)
    9. [Make requests](#Make-requests)
    10. [Publish to Azure Container Registry](#Publish-to-Azure-Container-Registry)
    11. [Run your container in ACI](#Run-your-container-in-ACI)
    12. [FAQs](#FAQs)
3. [Grantee Onboarding Procedure](#Grantee-Onboarding-Procedure)
4. [Contributing](#Contributing)

## Repo Layout
- Containers
    - base-py [Base AI for Earth Python image]
        - nvidia/cuda:9.2 ubuntu 16.04 base
        - supervisor
        - miniconda3 4.5.4
        - Python 3.6.6
        - uwsgi
        - flask and flask-restful
        - azure-storage-blob
        - applicationinsights
        - AI for Earth task management tools
        - AI for Earth Azure SAS Blob tools
    - base-r [Base AI for Earth R image]
        - nvidia/cuda:9.2 ubuntu 16.04 base
        - supervisor
        - Python 3
        - Microsoft R Open 3.4.3
        - sp
        - gdal
        - plumber
        - future
        - reticulate
        - azure-storage-blob
        - applicationinsights
        - AI for Earth task management tools
        - AI for Earth Azure SAS Blob tools
    - blob-py [Base AI for Earth Python image with Azure Blob mounting tools]
        - AI for Earth base-py base
        - AI for Earth Azure Blob mounting tools
    - blob-r [Base AI for Earth R image with Azure Blob mounting tools]
        - AI for Earth base-r base
        - AI for Earth Azure Blob mounting tools
- Examples

## Notes
- Docker commands for the base and blob images must be run at the version level of the repo. Ex. `docker build . -f base-py/Dockerfile`.  Example Docker commands can be run within the example codebase.

# Quickstart
This quickstart will walk you through turning a model into an API.  Starting with a trained model, we will containerize it, deploy it on Azure, and expose an endpoint to call the API.  We will leverage Docker containers, Azure Application Insights, Azure Container Registry, and Azure Container Instances.  

## Choose a base image or example
AI for Earth APIs are all built from an AI for Earth base image.  You may use a base image directly or start with an example.  The following sections will help you decide.

### Base images
- base-py
- base-r
- blob-py
- blob-r

### Examples
- Basic Python API (Sync and Async)
- Basic R API (Sync and Async)
- Blob Python API
- Synchronous Custom Vision API (Python) 
- Synchronous PyTorch API

After you've chosen the example that best fits your scenario, make a copy of that directory, which you can use as your working directory in which you apply your changes.  

## Insert code to call your model
Next, in your new working directory, we need to update the example that you chose with code to call your specific model.  This should be done in the runserver.py file (if you are using a Python example) or the api_example.R file (if you are using an R example) in the my_api (or similarly named) subfolder.  

All examples contain the text "#INSERT_YOUR_MODEL_CALL_HERE".  This is intended to be a starting point to quickly get your API running with your model.  Simply adding your model will not perform necessary input checking, error handling, etc.

## Input handling

#### GET URL parameters
For GET operations, best practice dictates that a noun is used in the URL in the segment before the related parameter.  An echo example is as follows.

##### Python and Flask
```Python
@app.route(my_api_prefix + '/echo/<string:text>', methods=['GET'])
def echo(text):
    print(text)
```
##### R and Plumber
```R
#* @param text The text to echo back
#* @get /echo/<text>
GetProcessDataTaskStatus<-function(text){
  print(text)
}
```

#### POST body
For non-trivial parameters, retrieve parameters from the body sent as part of the request. [JSON](https://json.org/) is the preferred standard for API transmission. The following gives an example of sample input, followed by Python and R usage.

##### Sample Input
```JSON
{
    "container_uri": "https://myblobacct.blob.core.windows.net/user?st=2018-08-02T12%3A01%3A00Z&se=5200-08-03T12%3A01%3A00Z&sp=rwl&sv=2017-04-17&sr=c&sig=xxx",
    "run_id": "myrunid"
}
```

##### Python and Flask
```Python
from flask import Flask, request
import json

post_body = json.loads(request.data)

print(post_body['run_id'])
print(post_body['container_uri'])
```

##### R and Plumber
```R
library(jsonlite)

#* @post /process-data
ProcessDataAPI<-function(req, res){
  post_body <- req$postBody
  input_data <- fromJSON(post_body, simplifyDataFrame=TRUE)

  print(input_data$run_id)
  print(input_data$container_uri)
}
```

## Output handling
Two return types are important when dealing with hosted ML APIs: non-binary and binary.

#### Non-binary data
The preferred method to return non-binary data is to use JSON.

##### Python and Flask

```Python
import json
def post(self):
    ret = {}
    ret['run_id'] = 'myrunid'
    ret['container_uri'] = 'https://myblobacct.blob.core.windows.net/user?st=2018-08-02T12%3A01%3A00Z&se=5200-08-03T12%3A01%3A00Z&sp=rwl&sv=2017-04-17&sr=c&sig=xxx'

    return dumps(ret)
```

##### R and Plumber
```R
ProcessDataAPI<-function(req, res){
  post_body <- req$postBody
  input_data <- fromJSON(post_body, simplifyDataFrame=TRUE)

  # Return JSON containing run_id and container_uri 
  data.frame(input_data$run_id, input_data$container_uri)
}
```

#### Binary data
Binary data includes images.

##### Python and Flask

```Python
from io import BytesIO
import tifffile
from flask import send_file

ACCEPTED_CONTENT_TYPES = ['image/tiff', 'application/octet-stream']

if not request.headers.get("Content-Type") in ACCEPTED_CONTENT_TYPES:
    tiff_file = tifffile.imread(BytesIO(request.data))
    # Do something with the tiff_file...
    prediction_stream = BytesIO()
    # Create your image to return...
    prediction_stream.seek(0)
    return send_file(prediction_stream)
```
## Create AppInsights instrumentation keys
[Application Insights](https://docs.microsoft.com/en-us/azure/application-insights/app-insights-overview) is an Azure service for application performance management.  We have integrated with Application Insights to provide advanced monitoring capabilities.  

Create a new instance of Application Insights from the [Azure portal](https://portal.azure.com) and get your instrumentation key by following the instructions in the [below link](https://docs.microsoft.com/en-us/azure/application-insights/app-insights-create-new-resource) (you can stop after the "Copy the instrumentation key" step).  Then, follow the instructions from the [second link](https://docs.microsoft.com/en-us/azure/application-insights/app-insights-live-stream#sdk-requirements) to create a live stream key as well.  Store both of these keys in a safe place.   

- [Instrumentation key](https://docs.microsoft.com/en-us/azure/application-insights/app-insights-create-new-resource)

The instrumentation key is for general logging and tracing.  This is found under the "Properties" section for your Application Insights instance in the Azure portal. 
- [Live stream key](https://docs.microsoft.com/en-us/azure/application-insights/app-insights-live-stream#sdk-requirements)

The live stream key is used for traces and allows you to visualize a live stream of events within the Application Insights Azure Portal.

### Edit LocalForwarder.config
If you are using a Python-based image and would like to take advantage of tracing metrics, you will need to modify the LocalForwarder.config file by adding your Application Insights instrumentation and live stream keys.  There are three areas where you need to add your keys (be sure to add the proper key in the right place as shown below - you will use your instrumentation key twice and your live metrics key once):
```Xml
  <OpenCensusToApplicationInsights>
    <InstrumentationKey>your_instrumentation_key_goes_here</InstrumentationKey>
  </OpenCensusToApplicationInsights>
  <ApplicationInsights>
    <LiveMetricsStreamInstrumentationKey>your_instrumentation_key_goes_here</LiveMetricsStreamInstrumentationKey>
    <LiveMetricsStreamAuthenticationApiKey>your_live_metrics_key_goes_here</LiveMetricsStreamAuthenticationApiKey>
    ...
  </ApplicationInsights>
```

## Install required packages
Now, let's look at the Dockerfile in your code.  Update the Dockerfile to install any required packages. There are several ways to install packages.  We cover popular ones here:
- pip
```Dockerfile
RUN /usr/local/envs/ai4e_py_api/bin/pip install grpcio opencensus
```
- Anaconda
```Dockerfile
RUN echo "source activate ai4e_py_api" >> ~/.bashrc \
    && conda install -c conda-forge -n ai4e_py_api numpy pandas
```

- apt-get
```Dockerfile
RUN apt-get install gfortran -y
```

- R packages
```Dockerfile
RUN R -e 'install.packages("rgeos"); library(rgeos)'
```
## Set environment variables
The service_settings.env file contains several environment variables that should be set for proper logging.  Follow the instructions within the file.
```Dockerfile
# Logging Variables ----------------------------------------------------
# All logging and metric collection flows through Application Insights
# Set the following env var to your AppInsights instrumentation key.
APPINSIGHTS_INSTRUMENTATIONKEY=
# Optional live metrics stream key
# https://docs.microsoft.com/en-us/azure/application-insights/app-insights-live-stream#sdk-requirements
APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY=
# Location where AppInsights stores its data
LOCALAPPDATA=/app_insights_data
# Internal address of the OpenCensus tracer (for sending traces to AppInsights)
OCAGENT_TRACE_EXPORTER_ENDPOINT=localhost:55678
# The following variables will allow you to filter logs in AppInsights
SERVICE_OWNER=AI4E_Test
SERVICE_CLUSTER=Local Docker
SERVICE_MODEL_NAME=base-py example
SERVICE_MODEL_FRAMEWORK=Python
SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6
SERVICE_MODEL_VERSION=1.0
# End Logging Variables ------------------------------------------------

# Service Variables ----------------------------------------------------
# The API_PREFIX is the URL path that will occur after your domain and before your endpoints
API_PREFIX=/v1/my_api/tasker
# End Service Variables ----------------------------------------------------
```
You may modify other environment variables as well.  In particular, you may want to change the environment variable API_PREFIX.  We recommend using the format "/\<version-number>/\<api-name>/\<function>" such as "/v1/my_api/tasker".  

## Build and run your image
This section features a step-by-step guide to building and running your image.

### Build your image
1. Navigate to the directory containing your Dockerfile.
2. Execute the docker build command:
```Bash
docker build . -t your_custom_image_name:1
```
In the above command, -t denotes that you wish to label your image with the name "your_custom_image_name" and with the tag of 1.  Typically tags represent the build number.

If you will be pushing your image to a repository, your docker build command will resemble:
```Bash
docker build . -t your_registry_name.azurecr.io/your_custom_image_name:1
```

### Run your image, locally
Run a container based on your image:
```Bash
docker run --env-file=service_settings.env -p 8081:80 "customvisionsample:1"
```
In the above command, --env-file lets you pass in an environment variable file, the -p switch designates the local port mapping to the container port. -p host_port:container_port.  The host_port is arbitrary and will be the port to which you issue requests.  Ensure, however, that the container_port is exposed in the Dockerfile with the Dockerfile entry:
```Dockerfile
EXPOSE 80
```
TIP: Depending on your git settings and your operating system, the "docker run" command may fail with the error 'standard_init_linux.go:190: exec user process caused "no such file or directory"'.  If this happens, you need to change the end-of-line characters in startup.sh to LF.  One way to do this is using VS Code; open the startup.sh file and click on CRLF in the bottom right corner in the blue bar and select LF instead, then save.

If you find that there are errors and you need to go back and rebuild your docker container, run the following commands:
```Bash
# This lists all of the docker processes running
docker ps

# Find the container ID in the list from the previous command, and replace <container-id> with that value to end the process
docker kill <container-id> 
```


## Make requests
Now that you have a local instance of your contianer running, you should issue requests and debug it, locally.  For this exercise, you may issue requests in whatever way that you would like, but we prefer using [Postman](#https://www.getpostman.com/) to quickly test our endpoints.

### Test endpoints
1. Open Postman or your favorite API development tool.
2. From your service code, determine which endpoint you want to test.  If you are following one of our examples, the endpoint is: `http://localhost:<host_port>/<my_api_prefix>/<route>`.  Also, understand if you will issuing a POST or a GET.
3. In your API dev tool, select POST or GET and enter the endpoint you would like to test.
4. If you are performing a POST, construct valid JSON for your endpoint and enter it into the body of the request.
5. Click "Send" or execute the call to your endpoint.  The running container shell will contain any messages that are printed to the console.

## Publish to Azure Container Registry
If you haven't already, [create an instance of Azure Container Registry (ACR)](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal) in your subscription.  Note: if you just created an ACR, you will need to rebuild your container image with a tag that includes your ACR uri.

1. Log into your ACR:
```Bash
docker login --username <username> --password <password> <login server>
```
2. Push your image to your ACR:
```Bash
docker push your_registry_name.azurecr.io/your_custom_image_name:tag
```

## Run your container in Azure Container Instances
Running your container in ACI is easy.  The easiest way is to open the Azure Portal to your ACR, select the repository and tag that corresponds to the image you just pushed, click on it and select "Run Instance."  This will create a new ACI instance of your image.

### Issue requests to your hosted API
Now that your service is running within ACI, we can issue requests to it.
1. Open the Azure Portal to your ACI. Click on the "Overview" tab and copy the "IP address".
2. In your API tool, change localhost:port to the IP that you just copied.
3. Issue your request.

To see logs/console output in your running container, click on "Containers" in your ACI in the Azure Portal and click the "Logs" tab.  If you configured Application Insights, you may use that to review logs, identify issues, and view metrics.

## FAQs
- What is "my_api_prefix"?
"my_api_prefix" is a variable that denotes the prefix for all of your API endpoints.  Typically, you would create a versioned path, so that you can easily make breaking changes in the future without harming existing users.  A good prefix example would be: /v1/my_api/.
- In the Python example, why is there an "AppInsights" and an "AI4EAppInsights" library?
The Application Insights Python SDK is not an officially supported SDK, but it does provide great Flask integration.  Because of this, in our examples, we use the SDK's Flask integration, but we also provide a hardended (AI4EAppInsights) library that you should use for logging.

# Grantee Onboarding Procedure
AI for Earth Grantees may onboard their models/code to Azure and, in most cases, surface their solution as a private API or an AI for Earth API.  This section describes the fastest path to obtaining this result.

## Step 1: Identifying which container works with your technology stack
Currently, we offer two base image platform choices: Python and R and have an optional Azure Blob mounting capability available.

If you require an image with a different technology stack, we'd love to hear from you so we can expand our offerings.

## Step 2: Build an example service
To demonstrate how easy it is to run an API service in Azure, we'll explore the base-py example.

### Orientation
Under the examples/base-py directory, we find these objects:
- [my_api](./examples/base-py/my_api) folder [Contains the API service files.]
    - [runserver.py](./examples/base-py/my_api/runserver.py) [Contains the sample API service code.]
- [Dockerfile](./examples/base-py/Dockerfile) [A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image. This Dockerfile contains all the commands needed to run the example API service.]
- [LocalForwarder.config](./examples/base-py/LocalForwarder.config) [Application Insights tracing configuration. Replace your_key_goes_here with your actual key.]
- [startup.sh](./examples/base-py/startup.sh) [A simple bash script that is used as the service's entrypoint. We use a bash script as it allows us to easily run other required commands without having to expand the Dockerfile. See the blob-mount-py/startup.sh as an expanded example.]
- [supervisor.conf](./examples/base-py/supervisor.conf) [We use supervisor as our process control system. If your API service crashes, etc., supervisor will restart it for you. supervisor.conf holds the configuration necessary to execute supervisord, in the context of your API service.]

We explore the API file components via an outside-in approach, starting with the Dockerfile.

### [Dockerfile](./examples/base-py/Dockerfile)
If you are unfamiliar with Docker or container technologies, we enourage you to review the Docker [Get Started](https://docs.docker.com/get-started/) documentation.

Dockerfile walkthrough:

```Dockerfile 
FROM ai4eregistry.azurecr.io/1.0-base-py-ubuntu16.04:latest
```
- The very first line of our Dockerfile describes the base image, upon which we'll build our API service environment. In general, you may use any base image you would like, but if you wish to be considered as an AI For Earth API, you must use one of the official AI for Earth base images.  If you find that the provided base images are not sufficient, please connect with us so we may expand our offerings.
```Dockerfile 
RUN echo "source activate ai4e_py_api" >> ~/.bashrc \
    && conda install -c conda-forge -n ai4e_py_api numpy pandas
```
- All of the default packages have been installed within the Anaconda virtual environment: ai4e_py_api. Any additional necessary packages should be installed within this environment. This example demonstrates how to install numpy and pandas from the conda-forge package repository.

```Dockerfile
COPY ./my_api /app/my_api/
COPY ./supervisord.conf /etc/supervisord.conf
COPY ./startup.sh /
RUN chmod +x /startup.sh

COPY ./LocalForwarder.config /lf/
```
- Copy the API service directory into the container (your API service code will be placed in the /app/my_api directory).
- Copy the supervisor configuration file to the proper location.
- Copy the startup.sh bash script and add execute permission to it.

```Dockerfile 
ENV APPINSIGHTS_INSTRUMENTATIONKEY ''
ENV APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY  ''
ENV LOCALAPPDATA '/app_insights_data'
ENV OCAGENT_TRACE_EXPORTER_ENDPOINT 'localhost:55678'
ENV SERVICE_OWNER "AI4E_Test"
ENV SERVICE_CLUSTER "Local Docker"
ENV SERVICE_MODEL_NAME "base-py example"
ENV SERVICE_MODEL_FRAMEWORK "Python"
ENV SERVICE_MODEL_FRAMEOWRK_VERSION "3.6.6"
ENV SERVICE_MODEL_VERSION "1.0"
```
- All logging and metric collection flows through Application Insights. Set the APPINSIGHTS_INSTRUMENTATIONKEY environment varaible to your instrumentation key. This is required when offering an official AI for Earth API, but is highly suggested otherwise. If you wish not to use Application Insights, you can safely remove this line.  All of the SERVICE_ prefixed environment variables offer logging filters within Application Insights.


```Dockerfile
EXPOSE 80
ENTRYPOINT [ "/startup.sh" ]
```
- Expose the port that you wish to use to call your API.
- Specify the entrypoint, or the file to execute when starting the container.

### [supervisor.conf](./examples/base-py/supervisor.conf)
The supervisor.conf file contains a number of lines, but there are two that are important to execute your API service code.

`directory=/app/my_api/`
- If you modify the Dockerfile to place your code in a different directory than /app/my_api/, you must change it here.

Next, we look at the "command" specification.  This is a single line, but we'll break it apart for exploration. We example the important parts of the command, below:
`/usr/local/envs/ai4e_py_api/bin/uwsgi`
- uwsgi is used as our application server.  We point to its executable as the command. If you change the Anaconda virtual environment, you must change this line.

 `--virtualenv /usr/local/envs/ai4e_py_api`
 - Anaconda virtual environment declaration.

`--callable app`
- This your application name. Default is "app".

`--http 0.0.0.0:80`
- Specifices which port to use. Your API service will listen to this port. This port must be exposed in your Dockerfile.

`--wsgi-file /app/my_api/runserver.py`
- This is the location file in your API service code that contains your 'app' definition: `app = Flask(__name__)`

### [runserver.py](./examples/base-py/my_api/runserver.py)
This is an example entrypoint to an API service. We explore the important lines, below:
```Python
from ai4e_api_tools.task_management.api_task import ApiTaskManager
```
- The AI for Earth api toolset contains a task manager for use in long-running/async APIs services. The task manager stores state within the container, itself. Therefore, it is not a production-ready task manager. The task manager has been designed, however, to be directly pluggable into AI for Earth's distributed task manager. If you are designing your API for eventual adoption into the AI for Earth official APIs, utilizing this task manager will allow you to test your API and allow you to migrate to the AI for Earth distributed architecure without any code changes.

```Python
from ai4e_api_tools.ai4e_app_insights import AppInsights
```
- We have built a wrapper around the Application Insights Python API that allows us to quickly adopt your APIs into our offical API platform (without any code changes). If you wish to explore this option, please use this wrapper.

```Python
my_api_prefix = "/v1/my_api/tasker"
api_task_manager = ApiTaskManager(flask_api=api, resource_prefix=my_api_prefix)
```
- Creates the task manager, using the API path that is specified in my_api_prefix.

```Python
appinsights = AppInsights(app)
```
- Initialize the AI for Earth Application Insights class, which logs requests, traces and exceptions to your Application Insights service instance.

```Python
def post(self, msg=""):
    # Create a new long-running API task and set its status to 'queued'
    taskId = api_task_manager.AddTask('queued')
    # Log message to Application Insights
    app.logger.info('Queued task: ' + taskId)

    # Since we want to return the task information, create a thread to run the service code.
    thread = Thread(target = self.funct, args=(taskId))
    thread.start()
    return 'Starting task: ' + str(taskId)
```
- Set up a POST endpoint for your API.

```Python
def funct(self, taskId):
    api_task_manager.UpdateTaskStatus(taskId, 'started')
    sleep(10)  # replace with real code
    api_task_manager.UpdateTaskStatus(taskId, 'completed')
    app.logger.info('Completed task: ' + taskId)
```
- This is the method that actually runs your service code. Notice that we wrap the "real code" section with status updates. This allows the user to request status updates from the task GET endpoint - included via AI for Earth task management.

```Python
api.add_resource(Tasker, my_api_prefix)
```
- Maps the Tasker class as the API service class. Modify this prefix, when you want to change your endpoint prefix.

## Step 3: Run a service locally
Now that you have your container code completed, we can build your container and run it locally.

### Build an image
From within the context of your service directory (eg. ./examples/base-py), execute the command to build your image.
```Bash
docker build . -t <your_ACR_login_server>/<your_service_name>:<build_number>
```
So if we were to build our base-py example for use in the AI for Earth ACR:
```Bash
docker build . -t ai4eregistry.azurecr.io/grantee-py-example:1
```

### Run your container
```Bash
docker run -p <host port>:<container port> "<your_ACR_login_server>/<your_service_name>:<build_number>"
```
base-py example:
```Bash
docker run -p 8081:80 "ai4eregistry.azurecr.io/grantee-py-example:1"
```
Notice that, in the above example, we map our computer's port 8081 to the container's port 80. This reflects the container port we exposed in our Dockerfile and defined in the command in our supervisord.conf file.

If you need to log into the image while it's running to debug, etc.:
```Bash
docker ps  #shows you the running instances, find the CONTAINER ID of your container.
docker exec -it <container id> bash
```

## Step 4: Run a service in Azure
### Publish your image
To properly pull your image from within Kubernetes or Azure Container Instances, we must publish the image to a container registry. To get started using Azure Container Registry, please read this [quickstart](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-azure-cli).

```Bash
docker push <your_ACR_login_server>/<your_service_name>:<build_number>
```
base-py example:
```Bash
docker push ai4eregistry.azurecr.io/grantee-py-example:1
```
### Create and run your container
There are several ways to run your container in Azure. The easiest and fastest way to get up-and-running is to utilize Azure Container Instances (ACI). ACI gives us a few ways to deploy our container:
1. [Via the Azure CLI](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-azure-cli#deploy-image-to-aci)
2. [Via the Azure Portal](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal#deploy-image-to-aci)
3. [Via PowerShell](https://docs.microsoft.com/en-us/azure/container-registry/container-registry-get-started-powershell#deploy-image-to-aci)

# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit https://cla.microsoft.com.

When you submit a pull request, a CLA-bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., label, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.
