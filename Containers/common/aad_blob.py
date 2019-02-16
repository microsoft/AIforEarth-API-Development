# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from azure.storage.common import (
    TokenCredential
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

    def get_token_func(self):
        """
        This function makes a call to AAD to fetch an OAuth token
        :return: the OAuth token and the interval to wait before refreshing it
        """
        print("{}: token updater was triggered".format(datetime.datetime.now()))

        context = adal.AuthenticationContext(
            str.format("https://login.microsoftonline.com/{}", self.aad_tenant_id),
            api_version=None, validate_authority=True)

        oauth_token = context.acquire_token_with_client_credentials(
            "https://storage.azure.com",
            self.aad_application_id,
            self.aad_application_secret)

        return oauth_token['accessToken']

    def write_blob_from_text(self, container, blob, text):
        token_credential = TokenCredential(self.get_token_func())
        service = BlockBlobService(token_credential=token_credential, account_name=self.aad_account_name)
        service.create_blob_from_text(container, blob, text, 'utf-8')
        return service.make_blob_url(container, blob)

    def get_blob(self, container, blob):
        token_credential = TokenCredential(self.get_token_func())
        service = BlockBlobService(token_credential=token_credential, account_name=self.aad_account_name)

        with io.BytesIO() as output_stream:
            service.get_blob_to_stream(container, blob, output_stream)
            return output_stream

    def get_blob_to_bytes(self, container, blob):
        token_credential = TokenCredential(self.get_token_func())
        service = BlockBlobService(token_credential=token_credential, account_name=self.aad_account_name)
        blob = service.get_blob_to_bytes(container, blob)
        return blob.content

    def get_blob_to_text(self, container, blob):
        token_credential = TokenCredential(self.get_token_func())
        service = BlockBlobService(token_credential=token_credential, account_name=self.aad_account_name)
        blob = service.get_blob_to_text(container, blob)
        return blob.content

    def save_local_blob(self, container, blob, local_file):
        blob_bytes = self.get_blob_to_bytes(container, blob)
        f = open(local_file, 'wb')
        f.write(blob_bytes)
        f.close()

    def get_blob_uri(self, container, blob):
        print("contianer: " + container + ", blob: " + blob)
        token_credential = TokenCredential(self.get_token_func())
        service = BlockBlobService(token_credential=token_credential, account_name=self.aad_account_name)
        url = service.make_blob_url(container, blob)
        print("url: " + url)
        return url