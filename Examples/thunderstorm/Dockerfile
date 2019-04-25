FROM mcr.microsoft.com/aiforearth/base-py:1.4

# Example of installing additonal Anaconda packages - numpy and pandas
RUN echo "source activate ai4e_py_api" >> ~/.bashrc \
    && conda install -c conda-forge -n ai4e_py_api numpy pandas scikit-learn matplotlib

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/runserver.py) is renamed, you must change supervisor.conf
# Copy your API code
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
    SERVICE_MODEL_NAME=base-py\ example \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 \
    ENVSERVICE_MODEL_VERSION=1.0

ENV MODEL_PATH=/app/thunderstorm_rotation/sklearn_model.pkl
ENV API_PREFIX=/v1/thunderstorm

COPY ./thunderstorm_rotation /app/thunderstorm_rotation/

# Expose the port that is to be used when calling your API
EXPOSE 1212
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost:1212/${API_PREFIX}/ || exit 1
ENTRYPOINT [ "/startup.sh" ]