# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from datetime import datetime
import json
import os
import multiprocessing
from typing import Any, Dict
import uuid

import requests


print("Creating task manager.")

LOCAL_BLOB_TEST_DIRECTORY = os.getenv('LOCAL_BLOB_TEST_DIRECTORY', '.')

class TaskManager:

    # use a lock whenever we access task_status.json
    task_status_json_lock = multiprocessing.Lock()

    def __init__(self):
        self.status_dict = {}
        self.task_status_json_path = os.path.join(
            LOCAL_BLOB_TEST_DIRECTORY, 'task_status.json')

    def GetTaskId(self) -> str:
        return str(uuid.uuid4())

    def AddTask(self, request):
        status = {
            'TaskId': self.GetTaskId(),
            'Status': 'created',
            'Timestamp': datetime.strftime(
                datetime.utcnow(), "%Y-%m-%d %H:%M:%S"),
            'Endpoint': request.path
        }

        with self.task_status_json_lock:
            statuses = []
            if os.path.isfile(self.task_status_json_path):
                with open(self.task_status_json_path, 'r') as f:
                    statuses = json.load(f)
            statuses.append(status)

            with open(self.task_status_json_path, 'w') as f:
                json.dump(statuses, f)
        return status

    def UpdateTaskStatus(self, taskId: str, status: Any) -> None:
        with self.task_status_json_lock:
            if not os.path.isfile(self.task_status_json_path):
                raise ValueError('taskId "{}" is not found. Decorate your endpoint with an ai4e_service decorator or call AddTask(request) before UpdateTaskStatus.'.format(taskId))

            statuses = []
            with open(self.task_status_json_path, 'r') as f:
                statuses = json.load(f)

            task_status = None
            for rec_status in statuses:
                if rec_status['TaskId'] == taskId:
                    task_status = rec_status
                    break

            if task_status is None:
                raise ValueError('taskId "{}" is not found. Decorate your endpoint with an ai4e_service decorator or call AddTask(request) before UpdateTaskStatus.'.format(taskId))
            else:
                task_status['Status'] = status
                task_status['Timestamp'] = datetime.strftime(
                    datetime.utcnow(), "%Y-%m-%d %H:%M:%S")

            with open(self.task_status_json_path, 'w') as f:
                json.dump(statuses, f)

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

    def GetTaskStatus(self, taskId: str) -> Dict[str, Any]:
        with self.task_status_json_lock:
            if os.path.isfile(self.task_status_json_path):
                with open(self.task_status_json_path, 'r') as f:
                    statuses = json.load(f)

                for rec_status in statuses:
                    if rec_status['TaskId'] == taskId:
                        return rec_status

        status = {
            'TaskId': taskId,
            'Status': 'Not found.',
            'Timestamp': datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"),
            'Endpoint': ''
        }
        return status
