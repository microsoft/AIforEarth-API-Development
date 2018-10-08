#ai4eregistry.azurecr.io/1.0-base-py-ubuntu16.04:subversion
FROM nvidia/cuda:9.2-runtime-ubuntu16.04

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV PATH /opt/conda/bin:$PATH
RUN mkdir /var/uwsgi

RUN apt-get update --fix-missing && \
    apt-get install -y wget supervisor bzip2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get -qq update && apt-get -qq -y install curl bzip2 \ 
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-4.5.4-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \ 
    && rm -rf /tmp/miniconda.sh \ 
    && conda install -y python=3 \ 
    && conda update conda \ 
    && apt-get -qq -y remove curl bzip2 \ 
    && apt-get -qq -y autoremove \ 
    && apt-get autoclean \ 
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \ 
    && conda clean --all --yes

RUN conda create -n ai4e_py_api python=3.6.6 \
    && echo "source activate ai4e_py_api" >> ~/.bashrc \
    && conda install -c conda-forge -n ai4e_py_api uwsgi flask flask-restful

# Install Azure Blob SDK
RUN /usr/local/envs/ai4e_py_api/bin/pip install azure \
    && /usr/local/envs/ai4e_py_api/bin/pip install azure-storage-blob

# Install opencensus and Application Insights Local Forwarder for monitoring
RUN wget -q https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb
RUN dpkg -i packages-microsoft-prod.deb

RUN apt-get install apt-transport-https -y \
    && apt-get update \
    && apt-get install aspnetcore-runtime-2.1 -y

RUN /usr/local/envs/ai4e_py_api/bin/pip install grpcio opencensus

RUN mkdir /lf

RUN apt-get update && apt-get install -y --no-install-recommends \
		ca-certificates \
		curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -L \
    --retry 5 \
    --retry-delay 0 \
    --retry-max-time 40 \
     'https://github.com/Microsoft/ApplicationInsights-LocalForwarder/releases/download/v0.1-beta1/LF-ConsoleHost-linux-x64.tar.gz' \
    -o /lf/LF-ConsoleHost-linux-x64.tar.gz

RUN tar -xvzf /lf/LF-ConsoleHost-linux-x64.tar.gz -C /lf/

RUN chmod +x /lf/Microsoft.LocalForwarder.ConsoleHost

EXPOSE 55678
EXPOSE 50001

RUN /usr/local/envs/ai4e_py_api/bin/pip install applicationinsights

ENV PATH /usr/local/envs/ai4e_py_api/bin:$PATH

COPY ./base-py/ai4e_api_tools /ai4e_api_tools/
COPY ./common/sas_blob.py /ai4e_api_tools/

RUN mkdir /app_insights_data
RUN chmod +w /app_insights_data

ENV PYTHONPATH="${PYTHONPATH}:/ai4e_api_tools"