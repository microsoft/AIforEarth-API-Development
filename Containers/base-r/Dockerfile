# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#mcr.microsoft.com/aiforearth/base-r:version
FROM osgeo/gdal:ubuntu-full-3.0.3
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update --fix-missing && \
    apt-get install -y wget supervisor bzip2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		r-base \
		r-base-dev \
    r-recommended

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
        software-properties-common \
        wget \
        xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN add-apt-repository 'deb [arch=amd64,i386] https://cran.rstudio.com/bin/linux/ubuntu bionic-cran35/'

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		r-base \
		r-base-dev \
    r-recommended

RUN echo "r <- getOption('repos'); r['CRAN'] <- 'http://cran.r-project.org'; options(repos = r);" > ~/.Rprofile
RUN Rscript -e 'install.packages(c("curl", "httr"));'
RUN Rscript -e 'Sys.setenv(CURL_CA_BUNDLE="/utils/microsoft-r-open-3.4.3/lib64/R/lib/microsoft-r-cacert.pem");'
RUN Rscript -e 'install.packages("sp");'
RUN Rscript -e 'install.packages("rgdal");'
RUN Rscript -e 'install.packages("plumber");'
RUN Rscript -e 'install.packages("R.utils");'
RUN Rscript -e 'install.packages("future");'
RUN Rscript -e 'install.packages("devtools");'
RUN Rscript -e 'install.packages("RCurl");'
RUN Rscript -e 'install.packages("sjmisc");'
RUN Rscript -e 'install.packages("reticulate");'
RUN Rscript -e 'install.packages("urltools");'
RUN Rscript -e 'install.packages("ids");'

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip
  
COPY ./base-py/requirements.txt /ai4e_api_tools/
WORKDIR /ai4e_api_tools
RUN pip3 install -r ./requirements.txt

COPY ./base-r/ai4e_api_tools /ai4e_api_tools/
COPY ./common/sas_blob.py /ai4e_api_tools/
COPY ./common/aad_blob.py /ai4e_api_tools/

ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"