FROM mcr.microsoft.com/aiforearth/base-py:latest

# Example of installing additonal Anaconda packages - numpy and pandas
RUN echo "source activate ai4e_py_api" >> ~/.bashrc \
    && conda install -c conda-forge -n ai4e_py_api numpy pandas

RUN /usr/local/envs/ai4e_py_api/bin/pip install --upgrade pip

RUN /usr/local/envs/ai4e_py_api/bin/pip install tensorflow pillow

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/runserver.py) is renamed, you must change supervisor.conf
COPY ./supervisord.conf /etc/supervisord.conf
# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

COPY ./LocalForwarder.config /lf/

# Copy your API code
COPY ./tf_iNat_api /app/tf_iNat_api/

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY=
ENV LOCALAPPDATA=/app_insights_data OCAGENT_TRACE_EXPORTER_ENDPOINT=localhost:55678

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_PyTorch_Example SERVICE_CLUSTER=Local\ Docker \
  SERVICE_MODEL_NAME=AI4E_PyTorch_Example SERVICE_MODEL_FRAMEWORK=Python \
  SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 SERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/tf_iNat_api

ENV STORAGE_ACCOUNT_NAME= STORAGE_ACCOUNT_KEY=

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/ || exit 1
ENTRYPOINT [ "/startup.sh" ]
