FROM ai4eregistry.azurecr.io/1.0-base-py-ubuntu16.04:latest

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

# Logging ------------------------------------------------------------
# All logging and metric collection flows through Application Insights
# Set the following env var to your AppInsights instrumentation key.
ENV APPINSIGHTS_INSTRUMENTATIONKEY ''
# Optional live metrics stream key, https://docs.microsoft.com/en-us/azure/application-insights/app-insights-live-stream#sdk-requirements
ENV APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY ''
# Location where AppInsights stores its data
ENV LOCALAPPDATA '/app_insights_data'
# Internal address of the OpenCensus tracer (for sending traces to AppInsights)
ENV OCAGENT_TRACE_EXPORTER_ENDPOINT 'localhost:55678'
# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER "AI4E_Custom_Vision_Example"
ENV SERVICE_CLUSTER "Local Docker"
ENV SERVICE_MODEL_NAME "customvision-sample"
ENV SERVICE_MODEL_FRAMEWORK "Python"
ENV SERVICE_MODEL_FRAMEOWRK_VERSION "3.6.6"
ENV SERVICE_MODEL_VERSION "1.0"
# Logging End ---------------------------------------------------------

# Custom Vision configuration
ENV CUSTOM_VISION_PREDICTION_KEY ''
ENV CUSTOM_VISION_PROJECT_ID ''
ENV CUSTOM_VISION_ITERATION_ID ''

ENV API_PREFIX '/v1/customvision/predict'

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/ || exit 1
ENTRYPOINT [ "/startup.sh" ]
