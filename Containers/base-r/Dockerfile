#ai4eregistry.azurecr.io/1.0-base-r-ubuntu16.04:subversion
FROM nvidia/cuda:9.2-runtime-ubuntu16.04
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

# Install Azure Blob SDK
RUN pip install azure \
    && pip install azure-storage-blob

# Install Application Insights for monitoring
RUN pip install applicationinsights

RUN apt-get update \
&& apt-get install -y \
  apt-transport-https \
  build-essential \
  ed \
  gtk2.0 \
  libcurl4-openssl-dev \
  libgtk2.0-dev \
  libiodbc2-dev \
  libnlopt-dev \
  libssh2-1-dev \
  libssl-dev \
  libxml2-dev \
  python-dev \
  python-software-properties \
  software-properties-common \
  wget \
  xvfb \
  supervisor \
&& rm -rf /var/lib/apt/lists/*

RUN wget -O rtvs-daemon.tar.gz https://aka.ms/r-remote-services-linux-binary-current && \
    mkdir ./rtvsd && \
    tar -xvzf rtvs-daemon.tar.gz -C ./rtvsd && \
    ./rtvsd/rtvs-install -s

RUN mkdir /tmp/mro && cd /tmp/mro \
  && wget -O microsoft-r-open.tar.gz https://mran.blob.core.windows.net/install/mro/3.4.3/microsoft-r-open-3.4.3.tar.gz \
  && tar -xvzf microsoft-r-open.tar.gz \
  && /tmp/mro/microsoft-r-open/install.sh --accept-mkl-eula -u

RUN apt-get update -qq && apt-get install -y \
  git-core \
  libssl-dev \
  libcurl4-gnutls-dev

# Install data_processing packages
RUN apt-get update && \
    apt-get install -y \
    libgdal-dev \
    libproj-dev

RUN R -e 'install.packages("sp"); library(sp)'
RUN R -e 'install.packages("rgdal"); library(rgdal)'

# Install plumber (REST-based serving in R): https://github.com/trestletech/plumber
RUN R -e 'install.packages("plumber"); library(plumber)'

# Install future package for async
RUN R -e 'install.packages("R.utils");'
RUN R -e 'install.packages("future");'

RUN R -e 'remove.packages(c("curl","httr"));'
RUN R -e 'install.packages(c("curl", "httr"))'
RUN R -e 'Sys.setenv(CURL_CA_BUNDLE="/utils/microsoft-r-open-3.4.3/lib64/R/lib/microsoft-r-cacert.pem")'

RUN R -e 'install.packages("devtools");'
RUN R -e 'install.packages("RCurl");'
RUN R -e 'install.packages("sjmisc");'

RUN apt-get update \
&& apt-get install -y \
  unzip
RUN R -e 'devtools::install_github("rstudio/reticulate");'

COPY ./base-r/ai4e_api_tools /ai4e_api_tools/
COPY ./common/sas_blob.py /ai4e_api_tools/

RUN mkdir /app_insights_data
RUN chmod +w /app_insights_data

ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"

EXPOSE 443