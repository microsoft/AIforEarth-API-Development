# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import uuid
import io
from datetime import datetime, timedelta
from urllib.parse import urlsplit, urlparse

from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient, generate_container_sas, ContainerSasPermissions, ContainerClient, BlobClient

class SasBlob:
    def _get_resource_reference(self, prefix):
        return '{}{}'.format(prefix, str(uuid.uuid4()).replace('-', ''))

    def get_container_from_uri(self, sas_uri):
        url_parts = urlsplit(sas_uri)

        raw_path = url_parts.path[1:]
        container = raw_path.split('/')[0]

        return  container

    def get_blob_from_uri(self, sas_uri):
        url_parts = urlsplit(sas_uri)

        raw_path = url_parts.path[1:]
        blob = raw_path.split('/')[1]

        return blob

    def get_sas_key_from_uri(self, sas_uri):
        url_parts = urlsplit(sas_uri)
        return url_parts.query

    def get_account_from_uri(self, sas_uri):
        url_parts = urlsplit(sas_uri)
        loc = url_parts.netloc
        return loc.split(".")[0]

    def delete_container(self, account_name, account_key, container_name):
        account_url = "https://{}.blob.core.windows.net".format(account_name)

        blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)
        blob_service_client.delete_container(container_name)

    def create_writable_container_sas(self, account_name, account_key, container_name, access_duration_hrs):
        account_url = "https://{}.blob.core.windows.net".format(account_name)

        blob_service_client = BlobServiceClient(account_url=account_url, credential=account_key)
        container_client = blob_service_client.create_container(container_name)

        sas_permissions = ContainerSasPermissions(read=True, write=True, delete=False, list=True)

        expiration = datetime.utcnow() + timedelta(hours=access_duration_hrs)

        sas_token = generate_container_sas(
            account_name,
            container_name,
            account_key=account_key,
            permission=sas_permissions,
            expiry=expiration
        )
        
        return '{}/{}?{}'.format(account_url, container_name, sas_token)

    def write_blob_from_bytes(self, container_sas_uri, blob_name, input_bytes):        
        container_client = ContainerClient.from_container_url(container_sas_uri)
        blob_client = container_client.get_blob_client(blob_name)

        blob_client.upload_blob(input_bytes, overwrite=True)
        
        account_name = self.get_account_from_uri(container_sas_uri)
        container_name = self.get_container_from_uri(container_sas_uri)
        sas_key = self.get_sas_key_from_uri(container_sas_uri)
        return 'https://{}.blob.core.windows.net/{}/{}?{}'.format(account_name, container_name, blob_name, sas_key)

    def write_blob_from_text(self, container_sas_uri, blob_name, text):
        container_client = ContainerClient.from_container_url(container_sas_uri)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(text, overwrite=True)

        account_name = self.get_account_from_uri(container_sas_uri)
        container_name = self.get_container_from_uri(container_sas_uri)
        sas_key = self.get_sas_key_from_uri(container_sas_uri)
        return 'https://{}.blob.core.windows.net/{}/{}?{}'.format(account_name, container_name, blob_name, sas_key)

    def write_blob(self, container_sas_uri, blob_name, input_stream):        
        container_client = ContainerClient.from_container_url(container_sas_uri)
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(input_stream, overwrite=True)
        
        account_name = self.get_account_from_uri(container_sas_uri)
        container_name = self.get_container_from_uri(container_sas_uri)
        sas_key = self.get_sas_key_from_uri(container_sas_uri)
        return 'https://{}.blob.core.windows.net/{}/{}?{}'.format(account_name, container_name, blob_name, sas_key)

    def get_blob(self, sas_uri):
        blob_client = BlobClient.from_blob_url(sas_uri)
        download_stream = blob_client.download_blob()

        with io.BytesIO() as output_stream:
            download_stream.readinto(output_stream)
            return output_stream

    def save_local_text(self, sas_uri, local_file):
        blob_client = BlobClient.from_blob_url(sas_uri)

        with open(local_file, "w") as open_file:
            download_stream = blob_client.download_blob(encoding='UTF-8')
            open_file.write(download_stream.readall())

    def get_blob_sas_uri(self, container_sas_uri, blob_name):
        account_name = self.get_account_from_uri(container_sas_uri)
        container_name = self.get_container_from_uri(container_sas_uri)
        sas_key = self.get_sas_key_from_uri(container_sas_uri)
        return 'https://{}.blob.core.windows.net/{}/{}?{}'.format(account_name, container_name, blob_name, sas_key)