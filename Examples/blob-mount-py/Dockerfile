FROM mcr.microsoft.com/aiforearth/blob-py:latest

# Copy blob connection information
COPY ./blob_mount.json /app/fuse/blob_mount.json

# Note: supervisor.conf reflects the location and name of your api code.
# If the default (./my_api/runserver.py) is renamed, you must change supervisor.conf
# Copy API code
COPY ./my_api /app/my_api/
COPY ./supervisord.conf /etc/supervisord.conf

# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

# Expose the port that is to be used when calling your API
EXPOSE 80
ENTRYPOINT [ "/startup.sh" ]