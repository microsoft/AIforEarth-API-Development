FROM ai4eregistry.azurecr.io/1.0-base-r-ubuntu16.04:latest

# Install fortran; required for adehabitat
RUN apt-get --assume-yes install gfortran

# Install some addtional R packages
RUN R -e 'install.packages("raster"); library(raster)'  
RUN R -e 'install.packages("maptools"); library(maptools)'
RUN R -e 'install.packages("ade4"); library(ade4)'
RUN R -e 'install.packages("rgeos"); library(rgeos)'
RUN R -e 'install.packages("adehabitatMA"); library(adehabitatMA)'
RUN R -e 'install.packages("adehabitatLT"); library(adehabitatLT)'
RUN R -e 'install.packages("trip"); library(trip)'
RUN R -e 'install.packages("adehabitatHR"); library(adehabitatHR)'

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/plumber_run.R) is renamed, you must change supervisor.conf
# Copy your API code
RUN mkdir -p /app/my_api/
WORKDIR /app/my_api/
COPY ./my_api/ /app/my_api/
COPY ./supervisord.conf /etc/supervisord.conf

# All logging and metric collection flows through Application Insights
# Set the following env var to your AppInsights instrumentation key.
ENV APPINSIGHTS_INSTRUMENTATIONKEY ''
# Optional live metrics stream key, https://docs.microsoft.com/en-us/azure/application-insights/app-insights-live-stream#sdk-requirements
ENV APPINSIGHTS_LIVEMETRICSSTREAMAUTHENTICATIONAPIKEY  ''
# Location where AppInsights stores its data
ENV LOCALAPPDATA '/app_insights_data'
# Internal address of the OpenCensus tracer (for sending traces to AppInsights)
ENV OCAGENT_TRACE_EXPORTER_ENDPOINT 'localhost:55678'
# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER "AI4E_Test"
ENV SERVICE_CLUSTER "Local Docker"
ENV SERVICE_MODEL_NAME "base-r example"
ENV SERVICE_MODEL_FRAMEWORK "R"
ENV SERVICE_MODEL_FRAMEOWRK_VERSION "microsoft-r-open-3.4.3"
ENV SERVICE_MODEL_VERSION "1.0"

# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

# Expose the port that is to be used when calling your API
EXPOSE 80
ENTRYPOINT [ "/startup.sh" ]

# Replace the above entrypoint with the following one for faster debugging.
#ENTRYPOINT ["R", "-e", "pr <- plumber::plumb(commandArgs()[4]); pr$run(host='0.0.0.0', port=80)"]
#CMD ["/app/my_api/api_example.R"]