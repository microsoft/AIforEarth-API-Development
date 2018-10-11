# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
library(future)
plan(multiprocess)
library(reticulate)
library(jsonlite)
use_virtualenv("ai4e_py_api")
source_python("/ai4e_api_tools/sas_blob.py")
source("/ai4e_api_tools/task_management/api_task.R")
source("/ai4e_api_tools/ai4e_app_insights.R")

request_being_processed <- FALSE

# Helper function to write dataframes to csv
WriteBlob <- function(dataframe_to_write, container_uri, blob_name, include_row_names) {
  sas_blob_helper = SasBlob()
  tmp <- file(tempfile())
  open(tmp, "w+")
  write.csv(dataframe_to_write, file=tmp, row.names = include_row_names, append=FALSE, fileEncoding="UTF-8")
  seek(tmp, where=0)
  data_to_save <- paste(readLines(tmp, n=-1), collapse="\n")
  sas_blob_helper$write_blob_from_text(container_uri, blob_name, data_to_save)
  close(tmp)
}

GetBlobFromContainer<-function(container_uri, blob_name){
  sas_blob_helper = SasBlob()
  input_data <- sas_blob_helper$get_blob_sas_uri(container_uri, blob_name)
  return(input_data)
}

# Primary working function
ProcessData<-function(taskId, config){
  tryCatch({
    # Update task status at any time
    UpdateTaskStatus(taskId, 'running')

    #INSERT_YOUR_MODEL_CALL_HERE

    container_uri <- config$container_uri

    run_id <- config$run_id
    observations_csv <- GetBlobFromContainer(container_uri, paste(run_id, "Observation.csv", sep= "/"))
    observations <- read.csv(observations_csv)

    dir = WriteBlob(observations, container_uri, paste(run_id, "output_dir/output_name.csv", sep= "/"), include_row_names=FALSE)

    UpdateTaskStatus(taskId, 'completed')
  }, error = function(err) {
    log_debug("Setting request_being_processed to FALSE.", taskId)
    request_being_processed <<- FALSE
    log_exception(paste0(err), taskId)
    UpdateTaskStatus(taskId, paste("failed - ", err))
  })
}

#* Test process
#* @post /test
function(req){
  print("running")

  task <- AddTask(req)
  taskId <- task$uuid
  sas_blob_helper = SasBlob()

  # R is single-threaded, so we only process one response at a time.
  # Parallel requests are handled by AKS auto-scaling.
  if (request_being_processed == TRUE)
  {
    log_warn("Too many requests are being processed.", taskId)
    res$status <- 429 # Too manay requests
    res$body <- "Too many requests are being processed. Retry with a backoff."
    return(res)
  }

  request_being_processed <<- TRUE

  tryCatch({
  body <- req$postBody
    input_data <- fromJSON(body, simplifyDataFrame=TRUE)

    promise <- future(ProcessData(taskId, input_data))
    message <- paste0("Starting task: ", taskId, " Output files will be placed in ", input_data$run_id, " directory.")
    directory <- input_data$run_id
  }, error = function(err) {
    log_debug("Setting request_being_processed to FALSE.", taskId)
    request_being_processed <<- FALSE
    log_exception(paste0(err), taskId)
    UpdateTaskStatus(taskId, paste("failed - ", err))
    res$status <- 400
    res$body <- "Bad request. Please ensure JSON request body is properly formatted."
    return(res)
  })

  data.frame(message, taskId, directory)
}

#* Get status of task by id
#* @param taskId The id of the task
#* @get /task/<taskId>
GetProcessDataTaskStatus<-function(taskId){
  status <- GetTaskStatus(taskId)
  return(status)
}

# Please have an empty last line in the end; otherwise, you will see an error when starting a webserver
