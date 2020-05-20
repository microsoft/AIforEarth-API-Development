FROM mcr.microsoft.com/aiforearth/base-py:1.13-cuda-9.0

RUN pip3 install tensorflow==1.12 pillow numpy pandas

# Copy your API code
COPY ./tf_iNat_api /app/tf_iNat_api/
COPY ./supervisord.conf /etc/supervisord.conf
# startup.sh is a helper script
COPY ./startup.sh /
RUN chmod +x /startup.sh

# Application Insights keys and trace configuration
ENV APPINSIGHTS_INSTRUMENTATIONKEY= \
    TRACE_SAMPLING_RATE=1.0

# The following variables will allow you to filter logs in AppInsights
ENV SERVICE_OWNER=AI4E_PyTorch_Example \
    SERVICE_CLUSTER=Local\ Docker \
    SERVICE_MODEL_NAME=AI4E_PyTorch_Example \
    SERVICE_MODEL_FRAMEWORK=Python \
    SERVICE_MODEL_FRAMEOWRK_VERSION=3.6.6 \
    SERVICE_MODEL_VERSION=1.0

ENV API_PREFIX=/v1/tf_iNat_api

ENV STORAGE_ACCOUNT_NAME= \
    STORAGE_ACCOUNT_KEY=

ENV PYTHONPATH="${PYTHONPATH}:/app/my_api/"
ENV PYTHONUNBUFFERED=TRUE

WORKDIR /app/tf_iNat_api

# Expose the port that is to be used when calling your API
EXPOSE 80
HEALTHCHECK --interval=1m --timeout=3s --start-period=20s \
  CMD curl -f http://localhost/${API_PREFIX}/  || exit 1
#ENTRYPOINT [ "/startup.sh" ]

# Use the following entrypoint to debug issues.
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:80", "runserver:app"]
