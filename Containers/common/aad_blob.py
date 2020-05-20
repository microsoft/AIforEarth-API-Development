# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from azure.identity import ClientSecretCredential, ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient, BlobClient

from datetime import datetime, timezone
from email.utils import formatdate
import adal
import io
import os
from shutil import copyfile
from pathlib import Path
import requests

CLIENT_SECRET_CRED_TYPE = "client_secret"
MANAGED_IDENTITY_CRED_TYPE = "managed_identity"
LOCAL_CRED_TYPE = "local"

# There are 3 ways to use this class:
#   1. ClientSecretCredential - provide aad_tenant_id, aad_application_id, aad_application_secret
#   2. ManagedIdentityCredential - provide aad_application_id. Application must be a managed identity: https://docs.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview
#   3. Local - provide local_test_directory. Circumvents AAD for testing purposes only.
class AadBlob:
    def __init__(self, aad_tenant_id=None, aad_application_id=None, aad_application_secret=None, aad_account_name=None, local_test_directory=None):
        self.aad_tenant_id = aad_tenant_id
        self.aad_application_id = aad_application_id
        self.aad_application_secret = aad_application_secret
        self.aad_account_name = aad_account_name
        self.local_test_directory=local_test_directory

        self.account_url="https://{}.blob.core.windows.net".format(self.aad_account_name)

        self.credential_type = LOCAL_CRED_TYPE
        if self.local_test_directory is None:
            if self.aad_application_secret is None:
                self.credential_type = MANAGED_IDENTITY_CRED_TYPE
            else:
                self.credential_type = CLIENT_SECRET_CRED_TYPE

    def _get_managed_identity_credential(self):
        cred = ManagedIdentityCredential(client_id=self.aad_application_id)
        return cred.get_token('https://storage.azure.com/.default').token

    def _get_blob_service_client(self):
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



    
    # Write Blobs............................
    def _upload_managed_identity_blob(self, container, blob, data):
        token_credential = self._get_managed_identity_credential()
        
        blob_uri = self.get_blob_uri(container, blob)

        headers = { 'Authorization': 'Bearer ' + token_credential,
                    'x-ms-version': '2019-07-07',
                    'x-ms-date': formatdate(timeval=None, localtime=False, usegmt=True),
                    'x-ms-blob-type': 'BlockBlob',
                    'Content-Length': str(len(data))}

        r = requests.put(blob_uri, headers=headers, data=data)
        r.raise_for_status()
        return r

    def _write_blob(self, container, blob, data):
        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            get_response = self._upload_managed_identity_blob(container, blob, data)
            return get_response

        else: # CLIENT_SECRET_CRED_TYPE:
            blob_service_client = self._get_blob_service_client()
            blob_client = blob_service_client.get_blob_client(container, blob)
            blob_client.upload_blob(data, overwrite=True)

    def write_blob_from_text(self, container, blob, text):
        print("{} for {}/{}".format('write_blob_from_text', container, blob))

        if not self.credential_type is LOCAL_CRED_TYPE:
            return self._write_blob(container, blob, text)

        else: # LOCAL_CRED_TYPE
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            if not os.path.exists(os.path.dirname(abosolute_file_name)):
                os.makedirs(os.path.dirname(abosolute_file_name))

            f = open(abosolute_file_name, 'w')
            f.write(text)
            f.close()
            return abosolute_file_name

    def create_blob_from_path(self, container, blob, path):
        print("{} for {}/{}".format('create_blob_from_path', container, blob))

        if not self.credential_type is LOCAL_CRED_TYPE:
            with open(path, "rb") as data:
                return self._write_blob(container, blob, data)

        else: # LOCAL_CRED_TYPE
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            if not os.path.exists(os.path.dirname(abosolute_file_name)):
                os.makedirs(os.path.dirname(abosolute_file_name))

            f = open(abosolute_file_name, 'wb')
            f.write(blob)
            f.close()
            return abosolute_file_name

    # Get Blobs............................
    def _download_managed_identity_blob(self, container, blob):
        token_credential = self._get_managed_identity_credential()
        
        blob_uri = self.get_blob_uri(container, blob)
        headers = { 'Authorization': "Bearer " + token_credential,
                    'x-ms-version': '2019-07-07',
                    'x-ms-date': formatdate(timeval=None, localtime=False, usegmt=True)}

        return requests.get(blob_uri, headers=headers)

    def _get_blob(self, container, blob, encoding = None):
        file_type = ('w' if encoding else 'wb')

        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            get_response = self._download_managed_identity_blob(container, blob)
            data = (get_response.text if encoding else get_response.content)
            return data

        else: # CLIENT_SECRET_CRED_TYPE:
            blob_service_client = self._get_blob_service_client()
            blob_client = blob_service_client.get_blob_client(container, blob)
            download_stream = blob_client.download_blob(encoding=encoding)
            return download_stream

    def save_blob_locally(self, container, blob, local_file, encoding = None):
        file_type = ('w' if encoding else 'wb')
        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            with open(local_file, file_type) as open_file:
                data = self._get_blob(container, blob, encoding)
                open_file.write(data)
                return str(get_response.headers)
                
        elif self.credential_type is CLIENT_SECRET_CRED_TYPE:
            with open(local_file, file_type) as open_file:
                data_stream = self._get_blob(container, blob, encoding)
                open_file.write(data_stream.readall())

        else: # LOCAL_CRED_TYPE
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            copyfile(abosolute_file_name, local_file)

    # Saves a binary blob locally
    def save_local_blob(self, container, blob, local_file):
        print("{} for {}/{}".format('save_local_blob', container, blob))
        return self.save_blob_locally(container, blob, local_file)

    # Saves a UTF-8 blob locally
    def save_local_text(self, container, blob, local_file):
        print("{} for {}/{}".format('save_local_text', container, blob))
        return self.save_blob_locally(container, blob, local_file, encoding='UTF-8')

    # Gets a blob to a stream
    def get_blob(self, container, blob):
        print("{} for {}/{}".format('get_blob', container, blob))

        if self.credential_type is CLIENT_SECRET_CRED_TYPE:
            blob_service_client = self._get_blob_service_client()
            blob_client = blob_service_client.get_blob_client(container, blob)

            with io.BytesIO() as output_stream:
                download_stream = blob_client.download_blob()
                download_stream.readinto(output_stream)
                return output_stream
        else:
            abosolute_file_name = os.path.join('.', container, blob)

            if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
                self.save_blob_locally(container, blob, abosolute_file_name)
            else:
                abosolute_file_name = os.path.join(self.local_test_directory, container, blob)

            return open(abosolute_file_name)

    def get_blob_to_bytes(self, container, blob):
        print("{} for {}/{}".format('get_blob_to_bytes', container, blob))

        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            data = self._get_blob(container, blob)
            return data
        elif self.credential_type is CLIENT_SECRET_CRED_TYPE:
            data = self._get_blob(container, blob)
            return data.content_as_bytes()
        else: # LOCAL_CRED_TYPE
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            f = open(abosolute_file_name, 'rb')
            bi = f.read()
            f.close()
            return bi

    def get_blob_to_text(self, container, blob):
        print("{} for {}/{}".format('get_blob_to_text', container, blob))

        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            data = self._get_blob(container, blob, encoding='UTF-8')
            return data
        elif self.credential_type is CLIENT_SECRET_CRED_TYPE:
            data = self._get_blob(container, blob, encoding='UTF-8')
            return data.readall()
        else: # LOCAL_CRED_TYPE
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            print(abosolute_file_name)
            f = open(abosolute_file_name)
            txt = f.read()
            f.close()
            return txt


    # Helpers............................
    def does_blob_exist(self, container, blob):
        if self.credential_type is MANAGED_IDENTITY_CRED_TYPE:
            token_credential = self._get_managed_identity_credential()
            
            container_uri = "{}/{}?restype=container&comp=list&prefix{}".format(self.account_url, container, blob)

            headers = { 'Authorization': "Bearer " + token_credential,
                        'x-ms-version': '2019-07-07',
                        'x-ms-date': formatdate(timeval=None, localtime=False, usegmt=True)}

            blobs = requests.get(container_uri, headers=headers).json()
            if (len(blobs['Blobs']) > 0):
                return True
            else:
                return False

        elif self.credential_type is CLIENT_SECRET_CRED_TYPE:
            service = self._get_service()
            cc = service.get_container_client(container)
            blob_list = cc.list_blobs(name_starts_with=blob)
            for b in blob_list:
                if b.name == blob:
                    return True
            
            return False

        else: # LOCAL_CRED_TYPE
            abosolute_file_name = os.path.join(self.local_test_directory, container, blob)
            blobfile = Path(abosolute_file_name)
            return blobfile.exists()

    def get_blob_uri(self, container, blob):
        if self.local_test_directory is None:
            return "{}/{}/{}".format(self.account_url, container, blob)
        else:
            return os.path.join(self.local_test_directory, container, blob)

