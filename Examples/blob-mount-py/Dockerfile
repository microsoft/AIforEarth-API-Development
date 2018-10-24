FROM mcr.microsoft.com/aiforearth/blob-python:latest

# Copy blob connection information
COPY ./blob_mount.json /app/fuse/blob_mount.json

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/runserver.py) is renamed, you must change supervisor.conf
# Copy API code
COPY ./my_api /app/my_api/
COPY ./supervisord.conf /etc/supervisord.conf

# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY= \
    LOCALAPPDATA=/app_insights_data \
    OCAGENT_TRACE_EXPORTER_ENDPOINT=localhost:55678

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_Test \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=blob-mount-py\ example \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 \
    ENVSERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/my_api/mounter

# Expose the port that is to be used when calling your API
EXPOSE 80
ENTRYPOINT [ "/startup.sh" ]