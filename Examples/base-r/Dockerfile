FROM mcr.microsoft.com/aiforearth/base-r:latest

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

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/ || exit 1
#ENTRYPOINT [ "/startup.sh" ]

# Replace the above entrypoint with the following one for faster debugging.
ENTRYPOINT ["R", "-e", "pr <- plumber::plumb(commandArgs()[4]); pr$run(host='0.0.0.0', port=80)"]
CMD ["/app/my_api/api_example.R"]