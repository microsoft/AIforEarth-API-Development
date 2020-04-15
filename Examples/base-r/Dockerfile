FROM mcr.microsoft.com/aiforearth/base-r:1.6

# Install some addtional R packages
#RUN R -e 'install.packages("raster"); library(raster)'
RUN R -e 'print(installed.packages());'

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/plumber_run.R) is renamed, you must change supervisor.conf
# Copy your API code
RUN mkdir -p /app/my_api/
WORKDIR /app/my_api/
COPY ./my_api/ /app/my_api/
COPY ./supervisord.conf /etc/supervisord.conf

# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY=

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_Test \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=base-R\ example \
    SERVICE_MODEL_FRAMEWORK=R \
    SERVICE_MODEL_FRAMEOWRK_VERSION=microsoft-r-open-3.5.1 \
    SERVICE_MODEL_VERSION=1.0

ENV STORAGE_ACCOUNT_NAME ""
ENV STORAGE_ACCOUNT_KEY ""

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/ || exit 1
ENTRYPOINT [ "/startup.sh" ]

# Replace the above entrypoint with the following one for faster debugging.
#ENTRYPOINT ["R", "-e", "pr <- plumber::plumb(commandArgs()[4]); pr$run(host='0.0.0.0', port=80)"]
#CMD ["/app/my_api/api_example.R"]
