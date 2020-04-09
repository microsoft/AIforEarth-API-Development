# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import random, datetime
import os
import requests

print("Creating task manager.")

class TaskManager:
    def __init__(self):
        self.status_dict = {}

    def GetTaskId(self):
        id = str(random.randint(1, 10000))
        while id in self.status_dict:
            id = str(random.randint(1, 10000))
        return id

    def AddTask(self, request):
        id = self.GetTaskId()        
        self.status_dict[id] = ('created', datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"), 'task')

        ret = {}
        ret['TaskId'] = id
        ret['Status'] = self.status_dict[id][0]
        ret['Timestamp'] = self.status_dict[id][1]
        ret['Endpoint'] = self.status_dict[id][2]
        return(ret)

    def UpdateTaskStatus(self, taskId, status):
        if (taskId in self.status_dict):
            stat = self.status_dict[taskId]
            self.status_dict[taskId] = (status, stat[1], stat[2])
        else:
            self.status_dict[taskId] = (status, stat[1], stat[2])

        local_dir = os.getenv('LOCAL_BLOB_TEST_DIRECTORY', '')

        if os.path.exists(local_dir):
            append_write = 'a' # append if already exists
        else:
            append_write = 'w' # make a new file if not

        if len(local_dir) > 0:
            f = open(local_dir + '/task_status.txt', append_write)
            f.write(status)
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
        try:
            if taskId in self.status_dict:
                return self.status_dict[taskId]
            else:
                return "not found"
        except:
            print(sys.exc_info()[0])
