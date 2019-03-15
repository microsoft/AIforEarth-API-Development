# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import random, datetime
from flask_restful import Resource

print("Creating API task manager.")

class ApiTaskManager:
    def __init__(self, flask_api, resource_prefix = ""):
        self.resource_pfx = resource_prefix
        flask_api.add_resource(Task, self.resource_pfx + '/task/<int:id>', resource_class_kwargs={ 'task_manager': self })
        self.status_dict = {}

    def GetTaskId(self):
        id = str(random.randint(1, 10000))
        while id in self.status_dict:
            id = random.randint(1, 10000)
        return id

    def AddTask(self, request):
        id = self.GetTaskId()        
        self.status_dict[id] = ('created', datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S"), self.resource_pfx)

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

class Task(Resource):
    def __init__(self, **kwargs):
        self.task_mgr = kwargs['task_manager']

    def get(self, id):
        st = self.task_mgr.GetTaskStatus(str(id))
        ret = {}
        ret['uuid'] = id
        ret['status'] = st[0]
        ret['timestamp'] = st[1]
        ret['endpoint'] = "uri"
        return(ret)