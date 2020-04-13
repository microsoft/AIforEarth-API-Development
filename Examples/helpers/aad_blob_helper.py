from io import StringIO
from os import getenv
import tempfile
from aad_blob import AadBlob
import pandas as pd

aad_blob_connector = AadBlob(
                            getenv('AAD_TENANT_ID'),
                            getenv('AAD_APPLICATION_ID'),
                            getenv('AAD_APPLICATION_SECRET'),
                            getenv('AAD_ACCOUNT_NAME'),
                            getenv('LOCAL_BLOB_TEST_DIRECTORY', None))

class BlobHelper:
    def __init__(self, container_name, run_directory):
        self.aad_blob_connector = aad_blob_connector
        self.container_name = container_name
        self.run_directory = run_directory

    def write_csv(self, data, filename, top_directory, path = None):
        if (path is None):
            blob_name = '{}/{}/{}'.format(self.run_directory, top_directory, filename)
        else:
            blob_name = '{}/{}/{}/{}'.format(self.run_directory, top_directory, path, filename)

        csv_str = data.to_csv(encoding='utf-8')
        self.aad_blob_connector.write_blob_from_text(self.container_name, blob_name, csv_str.encode())

    def write_png(self, data, filename, top_directory, path = None):
        temp, temp_path = tempfile.mkstemp()

        data.savefig(temp_path)
        data.close()

        if (path is None):
            blob_name = '{}/{}/{}'.format(self.run_directory, top_directory, filename)
        else:
            blob_name = '{}/{}/{}/{}'.format(self.run_directory, top_directory, path, filename)

        self.aad_blob_connector.create_blob_from_path(self.container_name, blob_name, temp_path)

    def get_csv(self, csv_filename, top_directory, path = None):
        blob_name = ''
        if (path is None):
            blob_name = '{}/{}/{}'.format(self.run_directory, top_directory, csv_filename)
        else:
            blob_name = '{}/{}/{}/{}'.format(self.run_directory, top_directory, path, csv_filename)

        try:
            blob_text = self.aad_blob_connector.get_blob_to_text(self.container_name, blob_name)
        except Exception as e:
            print('Exception in get_csv:')
            print(e)
            raise ValueError('Blob: {} not found.'.format(blob_name))

        static_data = pd.read_csv(StringIO(blob_text))
        return static_data