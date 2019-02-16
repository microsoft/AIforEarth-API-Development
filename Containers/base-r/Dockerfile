#mcr.microsoft.com/aiforearth/base-r:version
FROM nvidia/cuda:9.2-runtime-ubuntu16.04
ARG DEBIAN_FRONTEND=noninteractive

RUN mkdir /var/uwsgi

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get update --fix-missing && \
    apt-get install -y wget supervisor bzip2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV GDAL_VERSION=2.2.1 

RUN apt-get update && \
    apt-get -y install \
        libpq-dev \
        ogdi-bin \
        libogdi3.2-dev \
        libjasper-runtime \
        libjasper-dev \
        libjasper1 \
        libgeos-dev \
        libproj-dev \
        libpoppler-dev \
        libsqlite3-dev \
        libspatialite-dev \
        python3 \
        python3-dev \
        python3-numpy

RUN wget http://download.osgeo.org/gdal/$GDAL_VERSION/gdal-${GDAL_VERSION}.tar.gz -O /tmp/gdal-${GDAL_VERSION}.tar.gz && \
    tar -x -f /tmp/gdal-${GDAL_VERSION}.tar.gz -C /tmp

RUN tar -xvf /tmp/gdal-${GDAL_VERSION}.tar.gz && cd /tmp/gdal-${GDAL_VERSION} \
    && ./configure \
    && make && make install && ldconfig \
    && apt-get update -y \
    && apt-get remove -y --purge build-essential wget \
    && rm -Rf $ROOTDIR/src/*

RUN rm /tmp/gdal-${GDAL_VERSION} -rf

CMD gdalinfo --version && gdalinfo --formats && ogrinfo --formats

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
RUN add-apt-repository 'deb [arch=amd64,i386] https://cran.rstudio.com/bin/linux/ubuntu xenial/'

RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
		r-base \
		r-base-dev \
    r-recommended

RUN apt-get update -qq && apt-get install -y \
  git-core \
  libssl-dev \
  libcurl4-gnutls-dev

# Install data_processing packages
RUN apt-get update && \
    apt-get install -y \
    libgdal-dev \
    libproj-dev

RUN echo "r <- getOption('repos'); r['CRAN'] <- 'http://cran.r-project.org'; options(repos = r);" > ~/.Rprofile
#RUN Rscript -e 'remove.packages(c("curl","httr"));'
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

# Install Azure Blob SDK and application insights
RUN pip install azure
RUN pip install azure-storage-common
RUN pip install azure-storage-blob
RUN pip install adal
RUN pip install applicationinsights

COPY ./base-r/ai4e_api_tools /ai4e_api_tools/
COPY ./common/sas_blob.py /ai4e_api_tools/
COPY ./common/aad_blob.py /ai4e_api_tools/

ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"