# Pull in the AI for Earth Base Image, so we can extract necessary libraries.
FROM mcr.microsoft.com/aiforearth/base-py:latest as ai4e_base

# Use any compatible Ubuntu-based image as your selected base image.
FROM nvidia/cuda:9.0-cudnn7-runtime-ubuntu16.04
# Copy the AI4E tools and libraries to our container.
COPY --from=ai4e_base /ai4e_api_tools /ai4e_api_tools
ENV PATH /usr/local/envs/ai4e_py_api/bin:$PATH
ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"

# Install Miniconda, Flask, Supervisor, uwsgi
RUN ./ai4e_api_tools/requirements/install-api-hosting-reqs.sh

# Install Opencensus
RUN ./ai4e_api_tools/requirements/install-opencensus.sh

# Install Application Insights
RUN ./ai4e_api_tools/requirements/install-appinsights.sh

RUN echo "source activate ai4e_py_api" >> ~/.bashrc \
    && conda install -c conda-forge -n ai4e_py_api numpy pandas
    
RUN /usr/local/envs/ai4e_py_api/bin/pip install --upgrade pip
RUN /usr/local/envs/ai4e_py_api/bin/pip install tensorflow==1.9 pillow requests_toolbelt

# Note: supervisor.conf reflects the location and name of your api code.
COPY ./supervisord.conf /etc/supervisord.conf
# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

COPY ./LocalForwarder.config /lf/
# Copy your API code
COPY ./animal-detector /app/animal-detector/

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY= \
    LOCALAPPDATA=/app_insights_data \
    OCAGENT_TRACE_EXPORTER_ENDPOINT=localhost:55678

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_Test \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=base-py\ example \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 \
    ENVSERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/animal_detection

ENV MODEL_PATH=/app/animal-detector/model/frozen_inference_graph.pb
ENV MODEL_VERSION=models/object_detection/faster_rcnn_inception_resnet_v2_atrous/megadetector

# Camera trap images are usually 4:3 width to height
# The config of the model in use (model/pipeline.config) has min_dimension
# 600 and max_dimension 1024 for the keep_aspect_ratio_resizer, which first resize an image so
# that the smaller edge is 600 pixels; if the longer edge is now more than 1024, it resizes such
# that the longer edge is 1024 pixels
# (https://github.com/tensorflow/models/issues/1794)
ENV MIN_DIM=600
ENV MAX_DIM=1024
ENV MAX_IMAGES_ACCEPTED=8
ENV GPU_BATCH_SIZE=8

ENV DEFAULT_DETECTION_CONFIDENCE=0.9

# Expose the port that is to be used when calling your API
EXPOSE 1212
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/ || exit 1
ENTRYPOINT [ "/startup.sh" ]