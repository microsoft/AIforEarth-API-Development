# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from flask import Flask
from flask_restful import Resource, Api
import os

print("Creating Application")
app = Flask(__name__)
api = Api(app)
blob_mapped_dir = "/mnt/input"

class ReadBlob(Resource):
    def read_blob_file(self, filename):
        data_path = os.path.join(blob_mapped_dir, filename)
        with open(data_path, "r") as file_from_blob:
            return file_from_blob.read()

    def get(self):
        filename = "config.csv"
        return "Blob file contents: " + self.read_blob_file(filename)

api.add_resource(ReadBlob, '/read_blob')

if __name__ == '__main__':
    app.run()
