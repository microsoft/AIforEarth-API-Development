#mcr.microsoft.com/aiforearth/blob-py:version
FROM mcr.microsoft.com/aiforearth/base-py:latest

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