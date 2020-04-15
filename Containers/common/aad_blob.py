# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

import datetime
import adal
import io
import os
from shutil import copyfile
from pathlib import Path

class AadBlob:
    def __init__(self, aad_tenant_id, aad_application_id, aad_application_secret, aad_account_name, local_test_directory=None):
        self.aad_tenant_id = aad_tenant_id
        self.aad_application_id = aad_application_id
        self.aad_application_secret = aad_application_secret
        self.aad_account_name = aad_account_name
        self.local_test_directory=local_test_directory

    def _get_service(self):
        token_credential = ClientSecretCredential(
            self.aad_tenant_id,
            self.aad_application_id,
            self.aad_application_secret
        )

        blob_service_client = BlobServiceClient(
            account_url="https://{}.blob.core.windows.net".format(self.aad_account_name),
            credential=token_credential
        )

        return blob_service_client

    def write_blob_from_text(self, container, blob, text):
        if self.local_test_directory is None:
            service = self._get_service()
            print("{} for {}/{}".format('write_blob_from_text', container, blob))
            
            blob = service.get_blob_client(container, blob)
            blob.upload_blob(text, overwrite=True)
        else:
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            if not os.path.exists(os.path.dirname(abosolute_file_name)):
                os.makedirs(os.path.dirname(abosolute_file_name))

            f = open(abosolute_file_name, 'w')
            f.write(text)
            f.close()
            return abosolute_file_name

    def create_blob_from_path(self, container, blob, path):
        if self.local_test_directory is None:
            service = self._get_service()
            print("{} for {}/{}".format('create_blob_from_path', container, blob))

            blob_client = service.get_blob_client(container, blob)
            with open(path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)
        else:
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            if not os.path.exists(os.path.dirname(abosolute_file_name)):
                os.makedirs(os.path.dirname(abosolute_file_name))

            f = open(abosolute_file_name, 'wb')
            f.write(blob)
            f.close()
            return abosolute_file_name

    def save_local_blob(self, container, blob, local_file):
        print("{} for {}/{}".format('save_local_blob', container, blob))
        service = self._get_service()
        if self.local_test_directory is None:
            blob_client = service.get_blob_client(container, blob)

            with open(local_file, "wb") as open_file:
                download_stream = blob_client.download_blob()
                open_file.write(download_stream.readall())
        else:
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            copyfile(abosolute_file_name, local_file)

    def save_local_text(self, container, blob, local_file):
        print("{} for {}/{}".format('save_local_blob', container, blob))
        service = self._get_service()
        if self.local_test_directory is None:
            blob_client = service.get_blob_client(container, blob)

            with open(local_file, "w") as open_file:
                download_stream = blob_client.download_blob(encoding='UTF-8')
                open_file.write(download_stream.readall())
        else:
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            copyfile(abosolute_file_name, local_file)


    def get_blob(self, container, blob):
        if self.local_test_directory is None:
            service = self._get_service()
            with io.BytesIO() as output_stream:
                print("{} for {}/{}".format('get_blob', container, blob))

                blob_client = service.get_blob_client(container, blob)
                download_stream = blob_client.download_blob()
                download_stream.readinto(output_stream)
                return output_stream
        else:
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            f = open(abosolute_file_name)
            return f

    def get_blob_to_bytes(self, container, blob):
        if self.local_test_directory is None:
            service = self._get_service()

            print("{} for {}/{}".format('get_blob_to_bytes', container, blob))
            blob_client = service.get_blob_client(container, blob)
            return blob_client.download_blob().content_as_bytes()
        else:
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            f = open(abosolute_file_name, 'rb')
            bi = f.read()
            f.close()
            return bi

    def get_blob_to_text(self, container, blob):
        if self.local_test_directory is None:
            service = self._get_service()
            print("{} for {}/{}".format('get_blob_to_text', container, blob))
            blob_client = service.get_blob_client(container, blob)
            download_stream = blob_client.download_blob(encoding='UTF-8')
            return download_stream.readall()
        else:
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            print(abosolute_file_name)
            f = open(abosolute_file_name)
            txt = f.read()
            f.close()
            return txt

    def get_blob_uri(self, container, blob):
        if self.local_test_directory is None:
            service = self._get_service()
            url = service.make_blob_url(container, blob)
            return url
        else:
            return os.path.join(self.local_test_directory, container, blob)

    def does_blob_exist(self, container, blob):
        if self.local_test_directory is None:
            service = self._get_service()
            cc = service.get_container_client(container)
            blob_list = cc.list_blobs(name_starts_with=blob)
            for b in blob_list:
                if b.name == blob:
                    return True
            
            return False
        else:
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            blobfile = Path(abosolute_file_name)
            return blobfile.exists()