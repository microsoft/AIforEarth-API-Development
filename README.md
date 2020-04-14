# AI for Earth - Creating APIs
These images and examples are meant to illustrate how to build containers for use in the AI for Earth API system. The following images and tags (versions/images) are available on Dockerhub:
- [mcr.microsoft.com/aiforearth/base-py](https://hub.docker.com/_/microsoft-aiforearth-base-py)
    - [Available Tags](https://mcr.microsoft.com/v2/aiforearth/base-py/tags/list)

- [mcr.microsoft.com/aiforearth/blob-r](https://hub.docker.com/_/microsoft-aiforearth-blob-r)
    - [Available Tags](https://mcr.microsoft.com/v2/aiforearth/blob-r/tags/list)

- [mcr.microsoft.com/aiforearth/blob-py](https://hub.docker.com/_/microsoft-aiforearth-blob-python)
    - [Available Tags](https://mcr.microsoft.com/v2/aiforearth/blob-python/tags/list)

- [mcr.microsoft.com/aiforearth/base-r](https://hub.docker.com/_/microsoft-aiforearth-base-r)
    - [Available Tags](https://mcr.microsoft.com/v2/aiforearth/base-r/tags/list)

## Notice
Additional to a running docker environment, GPU images require [NVIDIA Docker](https://github.com/nvidia/nvidia-docker) package to support CUDA.

### CUDA Toolkit

To view the license for the CUDA Toolkit included in the cuda base image, click [here](http://docs.nvidia.com/cuda/eula/index.html)

### CUDA Deep Neural Network library (cuDNN)

To view the license for cuDNN included in the cuda base image, click [here](https://developer.nvidia.com/cudnn/license_agreement)

## Contents
1. [Repo Layout](#repo-layout)
2. [Quickstart](#Quickstart)
3. [Grantee Onboarding Procedure](#Grantee-Onboarding-Procedure)
4. [Contributing](#Contributing)

## Repo Layout
- Containers
    - base-py [Base AI for Earth Python image]
        - API hosting libraries
        - Azure Blob libraries
        - Monitoring libraries
    - base-r [Base AI for Earth R image]
        - API hosting libraries
        - Azure Blob libraries
        - Monitoring libraries
    - blob-py [Base AI for Earth Python image with Azure Blob mounting tools]
        - AI for Earth base-py base
        - AI for Earth Azure Blob mounting tools
    - blob-r [Base AI for Earth R image with Azure Blob mounting tools]
        - AI for Earth base-r base
        - AI for Earth Azure Blob mounting tools
- Examples

## Notes
- Docker commands for the base and blob images must be run at the version level of the repo. Ex. `docker build . -f base-py/Dockerfile`.  Example Docker commands can be run within the example codebase.

# Quickstart Tutorial
A quickstart tutorial for converting a trained machine learning model to an API can be found at [Quickstart.md](Quickstart.md).  

# Grantee Onboarding Procedure
AI for Earth Grantees may onboard their models/code to Azure and, in most cases, surface their solution as a private API or an AI for Earth API.  This section describes the fastest path to obtaining this result.

## Step 1: Identifying which container works with your technology stack
Currently, we offer two base image platform choices: Python and R and have an optional Azure Blob mounting capability available.

If you require an image with a different technology stack, we'd love to hear from you so we can expand our offerings.

## Step 2: Build an example service
To demonstrate how easy it is to run an API service in Azure, we'll explore the `base-py` example.

### Orientation
Under the `examples/base-py` directory, we find these objects:
- [my_api](./examples/base-py) folder [Contains the API service files.]
    - [runserver.py](./examples/base-py/runserver.py) [Contains the sample API service code.]
- [Dockerfile](./examples/base-py/Dockerfile) [A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image. This Dockerfile contains all the commands needed to run the example API service.]
- [startup.sh](./examples/base-py/startup.sh) [A simple bash script that is used as the service's entrypoint. We use a bash script as it allows us to easily run other required commands without having to expand the Dockerfile. See the blob-mount-py/startup.sh as an expanded example.]
- [supervisor.conf](./examples/base-py/supervisor.conf) [We use supervisor as our process control system. If your API service crashes, etc., supervisor will restart it for you. supervisor.conf holds the configuration necessary to execute supervisord, in the context of your API service.]

We explore the API file components via an outside-in approach, starting with the Dockerfile.

### [Dockerfile](./examples/base-py/Dockerfile)
If you are unfamiliar with Docker or container technologies, we encourage you to review the Docker [Get Started](https://docs.docker.com/get-started/) documentation.

Dockerfile walkthrough:

```Dockerfile 
FROM mcr.microsoft.com/aiforearth/base-py:1.11
```
- The very first line of our Dockerfile describes the base image, upon which we'll build our API service environment. In general, you may use any base image you would like, but if you wish to be considered as an AI For Earth API, you must use one of the official AI for Earth base images.  If you find that the provided base images are not sufficient, please connect with us so we may expand our offerings.

```Dockerfile
COPY ./ /app/my_api/
COPY ./supervisord.conf /etc/supervisord.conf
COPY ./startup.sh /
RUN chmod +x /startup.sh
```
- Copy the API service directory into the container (your API service code will be placed in the `/app/my_api` directory).
- Copy the supervisor configuration file to the proper location.
- Copy the `startup.sh` bash script and add execute permission to it.

```Dockerfile 
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    TRACE_SAMPLING_RATE=1.0

ENV SERVICE_OWNER=AI4E_Test \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=base-py\ example \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.7 \
    ENVSERVICE_MODEL_VERSION=1.0 \
    DISABLE_CURRENT_REQUEST_METRIC=False
```
- All logging and metric collection flows through Application Insights. Set the APPINSIGHTS_INSTRUMENTATIONKEY environment variable to your instrumentation key. This is required when offering an official AI for Earth API, but is highly suggested otherwise. If you wish not to use Application Insights, you can safely remove this line.  All of the SERVICE_ prefixed environment variables offer logging filters within Application Insights.
- Set DISABLE_CURRENT_REQUEST_METRIC to True if you would like not record endpoint request denials.

```Dockerfile
ENV API_PREFIX=/v1/my_api/tasker
```
- Add a  URL prefix that your API will use.

```Dockerfile
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/ || exit 1
```
- The HEALTHCHECK will make a request to the / endpoint to ensure that the service is running. This is used by Docker to determine if the service is healthy.

```Dockerfile
EXPOSE 1212
ENTRYPOINT [ "/startup.sh" ]
```
- Expose the port that you wish to use to call your API.
- Specify the entrypoint, or the file to execute when starting the container.

### [supervisor.conf](./examples/base-py/supervisor.conf)
The supervisor.conf file contains a number of lines, but there are two that are important to execute your API service code.

`directory=/app/my_api/`
- If you modify the Dockerfile to place your code in a different directory than /app/my_api/, you must change it here.

Next, we look at the "command" specification.  This is a single line, but we'll break it apart for exploration. We example the important parts of the command, below:
`gunicorn`
- gunicorn is used as our application server.  We point to its executable as the command.

 `--workers 4`
 - The number of application server worker instances to run.

`runserver:app`
- This is the location file in your API service code that contains your 'app' definition: `app = Flask(__name__)`

### [runserver.py](./examples/base-py/my_api/runserver.py)
This is an main file that details your API service.

## Step 3: Run a service locally
Now that you have your container code completed, we can build your container and run it locally.

### Build an image
From within the context of your service directory (eg. .`/examples/base-py`), execute the command to build your image.
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
Notice that, in the above example, we map our computer's port `8081` to the container's port `80`. This reflects the container port we exposed in our Dockerfile and defined in the command in our supervisord.conf file.

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
