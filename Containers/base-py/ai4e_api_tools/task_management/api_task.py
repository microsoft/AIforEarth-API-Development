# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import random, datetime

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
        ret['uuid'] = id
        ret['status'] = self.status_dict[id][0]
        ret['timestamp'] = self.status_dict[id][1]
        ret['endpoint'] = self.status_dict[id][2]
        return(ret)

    def UpdateTaskStatus(self, taskId, status):
        if (taskId in self.status_dict):
            stat = self.status_dict[taskId]
            self.status_dict[taskId] = (status, stat[1], stat[2])
        else:
            self.status_dict[taskId] = (status, stat[1], stat[2])

    def AddPipelineTask(self, taskId, organization_moniker, version, api_name, body):
        next_url = organization_moniker + '/' + version + '/' + api_name
        UpdateTaskStatus(taskId, "Pipelining is not supported in a single node deployment, but the next service is: " + next_url)
        return "Pipelining is not supported in a single node deployment, but the next service is: " + next_url

    def CompleteTask(self, taskId, status):
        self.UpdateTaskStatus(taskId, status)

    def FailTask(self, taskId, status):
        self.UpdateTaskStatus(taskId, status)

    def GetTaskStatus(self, taskId):
        if taskId in self.status_dict:
            return self.status_dict[taskId]
        else:
            return "not found"