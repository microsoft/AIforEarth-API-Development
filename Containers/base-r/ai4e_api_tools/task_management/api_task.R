# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
AddTask<-function(req){
  taskId = 1

  newTask <- data.frame(
    uuid = taskId,
    status = c("queued"),
    timestamp = c(format(Sys.time(), "%b %d %X %Y")),
    endpoint = "uri"
  )

  if (file.exists("tasks.csv")) {
    print("file exists")
    tasks<-read.csv("tasks.csv", stringsAsFactors=FALSE)

    lastId <- tail(tasks, 1)[,1]
    taskId = lastId + 1
    newTask$uuid <- taskId
    
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
      uuid = taskId,
      status = c(status),
      timestamp = c(format(Sys.time(), "%b %d %X %Y")),
      endpoint = "uri"
    )

    write.csv(newTask, "tasks.csv", row.names=FALSE)
  }
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
