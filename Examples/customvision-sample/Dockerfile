FROM mcr.microsoft.com/aiforearth/base-py:latest

RUN pip install azure-cognitiveservices-vision-customvision

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/runserver.py) is renamed, you must change supervisor.conf
# Copy your API code
COPY ./custom_vision_api /app/custom_vision_api/
COPY ./supervisord.conf /etc/supervisord.conf
# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

COPY ./LocalForwarder.config /lf/

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY=
ENV LOCALAPPDATA=/app_insights_data OCAGENT_TRACE_EXPORTER_ENDPOINT=localhost:55678

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_Custom_Vision_Example SERVICE_CLUSTER=Local\ Docker \
  SERVICE_MODEL_NAME=customvision-sample SERVICE_MODEL_FRAMEWORK=Python \
  SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 SERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/customvision/predict

ENV CUSTOM_VISION_PREDICTION_KEY= CUSTOM_VISION_PROJECT_ID= \
  CUSTOM_VISION_ITERATION_ID=

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/ || exit 1
ENTRYPOINT [ "/startup.sh" ]
