# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from azure.storage.common import (
    TokenCredential,
    ExponentialRetry
)
from azure.storage.blob import (
    BlockBlobService,
)

import datetime
import adal
import io

class AadBlob:
    def __init__(self, aad_tenant_id, aad_application_id, aad_application_secret, aad_account_name):
        self.aad_tenant_id = aad_tenant_id
        self.aad_application_id = aad_application_id
        self.aad_application_secret = aad_application_secret
        self.aad_account_name = aad_account_name

    def _get_service(self):
        token_credential = TokenCredential(self.get_token_func())
        service = BlockBlobService(token_credential=token_credential, account_name=self.aad_account_name, socket_timeout=120)
        service.retry = ExponentialRetry(initial_backoff=5, increment_base=5, max_attempts=5).retry
        return service

    def get_token_func(self):
        """
        This function makes a call to AAD to fetch an OAuth token
        :return: the OAuth token and the interval to wait before refreshing it
        """
        context = adal.AuthenticationContext(
            str.format("https://login.microsoftonline.com/{}", self.aad_tenant_id),
            api_version=None, validate_authority=True)

        oauth_token = context.acquire_token_with_client_credentials(
            "https://storage.azure.com",
            self.aad_application_id,
            self.aad_application_secret)

        return oauth_token['accessToken']

    def callback(self, current, total):
        print("   progress: {} of {}".format(current, total))

    def write_blob_from_text(self, container, blob, text):
        service = self._get_service()
        print("{} for {}/{}".format('write_blob_from_text', container, blob))
        service.create_blob_from_text(container, blob, text, 'utf-8', max_connections=100, timeout=600, progress_callback=self.callback)
        return service.make_blob_url(container, blob)

    def create_blob_from_path(self, container, blob, path):
        service = self._get_service()
        print("{} for {}/{}".format('create_blob_from_path', container, blob))
        service.create_blob_from_path(container, blob, path, max_connections=100, timeout=600, progress_callback=self.callback)
        return service.make_blob_url(container, blob)

    def get_blob(self, container, blob):
        service = self._get_service()
        with io.BytesIO() as output_stream:
            print("{} for {}/{}".format('get_blob', container, blob))
            service.get_blob_to_stream(container, blob, output_stream, max_connections=100, timeout=600, progress_callback=self.callback)
            return output_stream

    def get_blob_to_bytes(self, container, blob):
        service = self._get_service()
        print("{} for {}/{}".format('get_blob_to_bytes', container, blob))
        blob = service.get_blob_to_bytes(container, blob, max_connections=100, timeout=600, progress_callback=self.callback)
        return blob.content

    def get_blob_to_text(self, container, blob):
        service = self._get_service()
        print("{} for {}/{}".format('get_blob_to_text', container, blob))
        blob = service.get_blob_to_text(container, blob, max_connections=100, timeout=600, progress_callback=self.callback)
        return blob.content

    def save_local_blob(self, container, blob, local_file):
        print("{} for {}/{}".format('save_local_blob', container, blob))
        blob_bytes = self.get_blob_to_bytes(container, blob)
        f = open(local_file, 'wb')
        f.write(blob_bytes)
        f.close()

    def get_blob_uri(self, container, blob):
        service = self._get_service()
        url = service.make_blob_url(container, blob)
        return url

    def does_blob_exist(self, container, blob):
        service = self._get_service()
        return service.exists(container, blob)