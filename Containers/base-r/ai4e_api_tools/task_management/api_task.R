# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
library(httr)

AddTask<-function(req){
  taskId = 1

  newTask <- data.frame(
    TaskId = taskId,
    Status = c("queued"),
    Timestamp = c(format(Sys.time(), "%b %d %X %Y")),
    Endpoint = "uri"
  )

  if (file.exists("tasks.csv")) {
    print("file exists")
    tasks<-read.csv("tasks.csv", stringsAsFactors=FALSE)

    lastId <- tail(tasks, 1)[,1]
    taskId = lastId + 1
    newTask$TaskId <- taskId
    
    write.csv(rbind(tasks, newTask), "tasks.csv", row.names=FALSE)
  }
  else {
    write.csv(newTask, "tasks.csv", row.names=FALSE)
  }

  return(newTask)
}

UpdateTaskStatus<-function(taskId, status){
  taskId = as.numeric(taskId)
  print(paste0("updating ", taskId, " to ", status))

  if (file.exists("tasks.csv")) {
    tasks<-read.csv("tasks.csv", stringsAsFactors=FALSE)

    tasks[taskId, 2] <- c(status)
    tasks[taskId, 3] <- c(format(Sys.time(), "%b %d %X %Y"))

    write.csv(tasks, "tasks.csv", row.names=FALSE)
  }
  else {
    newTask <- data.frame(
      TaskId = taskId,
      Status = c(status),
      Timestamp = c(format(Sys.time(), "%b %d %X %Y")),
      Endpoint = "uri"
    )

    write.csv(newTask, "tasks.csv", row.names=FALSE)
  }
}

CompleteTask<-function(taskId, status){
  UpdateTaskStatus(taskId, status)
}

FailTask<-function(taskId, status){
  UpdateTaskStatus(taskId, status)
}

AddPipelineTask<-function(taskId, organization_moniker, version, api_name, body) {
    next_url <- paste(version, organization_moniker, api_name, sep = "/")

    host <- Sys.getenv("LOCAL_NEXT_API_HOST_IN_PIPELINE")

    if (!is.empty(host)) {
      next_url <- paste(host, next_url, sep = "/")
    }

    tryCatch({
      res <- POST(next_url, body=body)

      if (status_code(r) != 200) {
        UpdateTaskStatus(taskId, paste0("Pipelining is not supported in a single node deployment, but the next service is: ", next_url))
        return(paste0("Pipelining is not supported in a single node deployment, but the next service is: ", next_url))
      }
    }, error = function(err) {
        print(err)
        UpdateTaskStatus(taskId, paste0("Pipelining is not supported in a single node deployment, but the next service is: ", next_url))
        return(paste0("Pipelining is not supported in a single node deployment, but the next service is: ", next_url))
    })

    return(res)
}

#* Get status of task by id
#* @param taskId The id of the task
#* @get /task/<taskId>
GetTaskStatus<-function(taskId){
  if (!file.exists("tasks.csv")) {
    return("Task not found.")
  }

  taskId = as.numeric(taskId)
  tasks<-read.csv("tasks.csv")
  tasks[taskId, 1:3]
}

# Please have an empty last line in the end; otherwise, you will see an error when starting a webserver
