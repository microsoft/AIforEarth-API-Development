# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import uuid
import time
import io
from datetime import datetime, timedelta
from urllib.parse import urlsplit, urlparse

from azure.storage.blob import (
    BlockBlobService,
    ContainerPermissions,
    BlobPermissions,
    PublicAccess,
    ContentSettings,
    BlobBlock,
    BlockListType,
)
from azure.storage.common import (
    AccessPolicy,
    ResourceTypes,
    AccountPermissions,
)

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

    def create_writable_container_sas(self, account_name, account_key, container_name, access_duration_hrs):
        block_blob_service = BlockBlobService(account_name=account_name, account_key=account_key)
 
        block_blob_service.create_container(container_name)

        token = block_blob_service.generate_container_shared_access_signature(
            container_name,
            ContainerPermissions.WRITE + ContainerPermissions.READ,
            datetime.utcnow() + timedelta(hours=access_duration_hrs))

        return block_blob_service.make_container_url(container_name=container_name, sas_token=token).replace("restype=container", "")

    def write_blob_from_bytes(self, sas_uri, blob_name, input_bytes):
        sas_service = BlockBlobService(
            account_name=self.get_account_from_uri(sas_uri),
            sas_token=self.get_sas_key_from_uri(sas_uri))

        container_name = self.get_container_from_uri(sas_uri)

        sas_service.create_blob_from_bytes(container_name, blob_name, input_bytes)

        return sas_service.make_blob_url(container_name, blob_name, sas_token=self.get_sas_key_from_uri(sas_uri))

    def write_blob_from_text(self, sas_uri, blob_name, text):
        sas_service = BlockBlobService(
            account_name=self.get_account_from_uri(sas_uri),
            sas_token=self.get_sas_key_from_uri(sas_uri))

        container_name = self.get_container_from_uri(sas_uri)

        sas_service.create_blob_from_text(container_name, blob_name, text, 'utf-8')

        return sas_service.make_blob_url(container_name, blob_name, sas_token=self.get_sas_key_from_uri(sas_uri))

    def write_blob(self, sas_uri, blob_name, input_stream):
        sas_service = BlockBlobService(
            account_name=self.get_account_from_uri(sas_uri),
            sas_token=self.get_sas_key_from_uri(sas_uri))

        container_name = self.get_container_from_uri(sas_uri)

        sas_service.create_blob_from_stream(container_name, blob_name, input_stream)

        return sas_service.make_blob_url(container_name, blob_name, sas_token=self.get_sas_key_from_uri(sas_uri))

    def get_blob(self, sas_uri):
        sas_service = BlockBlobService(
            account_name=self.get_account_from_uri(sas_uri),
            sas_token=self.get_sas_key_from_uri(sas_uri))

        with io.BytesIO() as output_stream:
            blob = sas_service.get_blob_to_stream(self.get_container_from_uri(sas_uri), self.get_blob_from_uri(sas_uri), output_stream)
            return blob

    def get_blob_sas_uri(self, container_sas_uri, blob_name, create_if_not_exists = False):
        container_name = self.get_container_from_uri(container_sas_uri)
        sas_service = BlockBlobService(
            account_name=self.get_account_from_uri(container_sas_uri),
            sas_token=self.get_sas_key_from_uri(container_sas_uri))
        blob_uri = sas_service.make_blob_url(container_name, blob_name, sas_token=self.get_sas_key_from_uri(container_sas_uri))

        return blob_uri