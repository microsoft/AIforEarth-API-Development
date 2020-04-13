# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import datetime
import os
import requests
import uuid
import json

print("Creating task manager.")

LOCAL_BLOB_TEST_DIRECTORY = os.getenv('LOCAL_BLOB_TEST_DIRECTORY', '.')

class TaskManager:
    def __init__(self):
        self.status_dict = {}

    def GetTaskId(self):
        return str(uuid.uuid4())

    def AddTask(self, request):
        id = self.GetTaskId()

        statuses = []
        if (os.path.isfile(LOCAL_BLOB_TEST_DIRECTORY + '/task_status.json')):
            with open(LOCAL_BLOB_TEST_DIRECTORY + '/task_status.json', 'r') as f:
                statuses = json.load(f)
                f.close()

        status = {}
        status['TaskId'] = id
        status['Status'] = 'created'
        status['Timestamp'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
        status['Endpoint'] = request.path

        statuses.append(status)

        with open(LOCAL_BLOB_TEST_DIRECTORY + '/task_status.json', 'w') as f:
                json.dump(statuses, f)
                f.close()
        return(status)

    def UpdateTaskStatus(self, taskId, status):
        statuses = []

        with open(LOCAL_BLOB_TEST_DIRECTORY + '/task_status.json', 'r') as f:
            statuses = json.load(f)
            f.close()

        for rec_status in statuses:
            if (rec_status['TaskId'] == taskId):
                rec_status['Status'] = status
                rec_status['Timestamp'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")

        with open(LOCAL_BLOB_TEST_DIRECTORY + '/task_status.json', 'w') as f:
            json.dump(statuses, f)
            f.close()

    def AddPipelineTask(self, taskId, organization_moniker, version, api_name, body):
        next_url = version + '/' + organization_moniker + '/' + api_name

        host = os.getenv('LOCAL_NEXT_API_HOST_IN_PIPELINE', '')

        if len(host) > 0:
            next_url = str(host) + '/' + str(next_url)

        r = requests.post(next_url, data=body)

        if r.status_code != 200:
            ai4e_service.api_task_manager.UpdateTaskStatus(taskId, "Pipelining is not supported in a single node deployment, but the next service is: " + next_url)
            return "Pipelining is not supported in a single node deployment, but the next service is: " + next_url
        else:
            return r.status_code

    def CompleteTask(self, taskId, status):
        self.UpdateTaskStatus(taskId, status)

    def FailTask(self, taskId, status):
        self.UpdateTaskStatus(taskId, status)

    def GetTaskStatus(self, taskId):
        if (os.path.isfile(LOCAL_BLOB_TEST_DIRECTORY + '/task_status.json')):
            with open(LOCAL_BLOB_TEST_DIRECTORY + '/task_status.json', 'r') as f:
                statuses = json.load(f)

                for rec_status in statuses:
                    if (rec_status['TaskId'] == taskId):
                        return rec_status
        status = {}
        status['TaskId'] = taskId
        status['Status'] = 'created'
        status['Timestamp'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
        status['Endpoint'] = ''
        return status
