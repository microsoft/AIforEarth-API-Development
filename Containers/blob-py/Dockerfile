#ai4eregistry.azurecr.io/1.0-blob-py-ubuntu16.04:subversion
FROM ai4eregistry.azurecr.io/1.0-base-py-ubuntu16.04:latest

#############################################################################################
# Add support for mounting an Azure blob
# Add the Microsoft package repository and install blobfuse
RUN wget https://packages.microsoft.com/config/ubuntu/16.04/packages-microsoft-prod.deb && \
    dpkg -i packages-microsoft-prod.deb && \
    apt-get update && \
    apt-get install blobfuse -y

COPY ./common/blob_mounting/blob_mounter.py /app/fuse/blob_mounter.py
RUN chmod +x /app/fuse/blob_mounter.py
#############################################################################################