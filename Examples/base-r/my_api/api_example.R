# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
library(future)
plan(multiprocess)
library(reticulate)
library(jsonlite)
use_python('/usr/bin/python3', required = TRUE)
source_python("/ai4e_api_tools/sas_blob.py")
source("/ai4e_api_tools/task_management/api_task.R")
source("/ai4e_api_tools/ai4e_app_insights.R")

write.table(paste0(FALSE), file = "running.txt")

STORAGE_ACCOUNT_NAME <- Sys.getenv("STORAGE_ACCOUNT_NAME")
STORAGE_ACCOUNT_KEY <- Sys.getenv("STORAGE_ACCOUNT_KEY")

# Helper function to write dataframes to csv
WriteBlob <- function(dataframe_to_write, container_uri, blob_name, include_row_names) {
  # Create a temp file stream to write the data.
  tmp <- file(tempfile())
  open(tmp, "w+")
  write.csv(dataframe_to_write, file=tmp, row.names = include_row_names, append=FALSE, fileEncoding="UTF-8")

  # Read the data to save to the blob.
  seek(tmp, where=0)
  data_to_save <- paste(readLines(tmp, n=-1), collapse="\n")

  # Upload the data to a blob using the AI for Earth sas_blob helper library.
  sas_blob_helper = SasBlob()
  sas_blob_helper$write_blob_from_text(container_uri, blob_name, data_to_save)
  close(tmp)
}

# Primary working function
ProcessData<-function(taskId, user_data){
  tryCatch({
    # Update task status at any time to let users know how your API is progressing.
    UpdateTaskStatus(taskId, 'running')

    # Get input data.
    container_name <- user_data$container_name
    run_id <- user_data$run_id

    # For this example, create a SAS-based writable container to use.
    access_duration_hrs <- 1
    sas_blob_helper <- SasBlob()
    container_sas_uri <- sas_blob_helper$create_writable_container_sas(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY, container_name, access_duration_hrs)
    print(paste("Container uri: ", container_sas_uri))

    observation_data_file <- "/app/my_api/Observations.csv"
    observation_data <- read.csv(observation_data_file)
    blob_name <- "Observations.csv"
    
    blob_sas_uri <- sas_blob_helper$write_blob_from_text(container_sas_uri, blob_name, observation_data)
    print(paste("Blob uri: ", blob_sas_uri))

    #INSERT_YOUR_MODEL_CALL_HERE

    # Download the Observation.csv from Azure Blob Storage and read it into observations.
    local_file <- "./local_observation.csv"
    observations_csv <- sas_blob_helper$save_local_text(blob_sas_uri, local_file)
    observations <- read.csv(local_file)

    # Write the observations output data to the output_dir/output_name.csv Azure Blob.
    #dir = WriteBlob(observations, container_sas_uri, paste(run_id, "output_dir/output_name.csv", sep= "/"), include_row_names=FALSE)

    # Update the task to let the caller know their request has been completed.
    UpdateTaskStatus(taskId, 'completed')
  }, error = function(err) {
    print(paste0(err))
    log_exception(paste0(err), taskId)
    UpdateTaskStatus(taskId, paste("failed - ", err))
    write.table(paste0(FALSE), file = "running.txt")
  })
}

#* Test process
#* @post /test
function(req){
  print("running")

  task <- AddTask(req)
  taskId <- task$uuid
  sas_blob_helper = SasBlob()

  is_processing <- read.table("running.txt")

  # R is single-threaded, so we only process one response at a time.
  # Parallel requests are handled by AKS auto-scaling.
  if (is_processing == "TRUE")
  {
    log_warn("Too many requests are being processed.", taskId)
    res$status <- 429 # Too manay requests
    res$body <- "Too many requests are being processed. Retry with a backoff."
    return(res)
  }

  write.table(paste0(TRUE), file = "running.txt")

  tryCatch({
    # Get the request body data and store into input_data.
    body <- req$postBody
    input_data <- fromJSON(body, simplifyDataFrame=TRUE)
    directory <- input_data$run_id

    # Run the model in a new "thread" so that we can return the taskId, which lets caller request the status at any time.
    #promise <- future(ProcessData(taskId, input_data))
    # Comment the above line and uncomment the below line to debug. taskId will not be returned until completion.
    ProcessData(taskId, input_data)
    message <- paste0("Starting task: ", taskId, " Output files will be placed in ", input_data$run_id, " directory.")
    
  }, error = function(err) {
    print(paste0(err))
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

#* Provide healthcheck endpoint
#* @get /
GetProcessDataTaskStatus<-function(taskId){
  return("OK")
}

# Please have an empty last line in the end; otherwise, you will see an error when starting a webserver
