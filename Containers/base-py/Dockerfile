#mcr.microsoft.com/aiforearth/base-py:version
ARG  BASE_IMAGE=nvidia/cuda:9.2-runtime-ubuntu16.04
FROM $BASE_IMAGE

ENV PATH /usr/local/envs/ai4e_py_api/bin:$PATH
ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"

RUN export LANG=C.UTF-8
RUN export LC_ALL=C.UTF-8

RUN apt-get update --fix-missing \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update \
    && apt-get install -y apt-utils \
        supervisor \
        curl \
        bzip2 \
        ca-certificates \
        libglib2.0-0 \
        libxext6 \
        libsm6 \
        libxrender1 \
        python3.7 \
        python3-setuptools \
        python3-dev \
        apt-transport-https \
        build-essential \
        gcc 

RUN easy_install3 pip

COPY ./base-py/requirements.txt /ai4e_api_tools/
WORKDIR /ai4e_api_tools
RUN pip3 install -r ./requirements.txt

# Install Azure Blob SDK
RUN pip3 install azure-mgmt-storage \
        azure-storage-blob \
        azure-identity

# Install Application Insights Opencensus packages
RUN pip3 install opencensus-ext-azure \
        opencensus-ext-flask

COPY ./base-py/ai4e_api_tools /ai4e_api_tools/
COPY ./common/sas_blob.py /ai4e_api_tools/
COPY ./common/aad_blob.py /ai4e_api_tools/
