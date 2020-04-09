# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Primary Application Insights R libary.

library(httr)
library(jsonlite)
library(sjmisc)

APP_SVC_URL <- "https://dc.services.visualstudio.com/v2/track"

APPINSIGHTS_INSTRUMENTATIONKEY <- Sys.getenv("APPINSIGHTS_INSTRUMENTATIONKEY")
CONF_SERVICE_OWNER <- Sys.getenv("SERVICE_OWNER", unset="")
CONF_SERVICE_CLUSTER <- Sys.getenv("SERVICE_CLUSTER", unset="")
CONF_SERVICE_MODEL_NAME <- Sys.getenv("SERVICE_MODEL_NAME", unset="")
CONF_SERVICE_MODEL_FRAMEWORK <- Sys.getenv("SERVICE_MODEL_FRAMEWORK", unset="")
CONF_SERVICE_MODEL_FRAMEOWRK_VERSION <- Sys.getenv("SERVICE_MODEL_FRAMEOWRK_VERSION", unset="")
CONF_SERVICE_MODEL_VERSION <- Sys.getenv("SERVICE_MODEL_VERSION", unset="")
CONF_SERVICE_NAME <- Sys.getenv("SERVICE_NAME", unset="")
CONF_SERVICE_VERSION <- Sys.getenv("SERVICE_VERSION", unset="")
CONF_SERVICE_CONTAINER_VERSION <- Sys.getenv("SERVICE_CONTAINER_VERSION", unset="")
CONF_SERVICE_CONTAINER_NAME <- Sys.getenv("SERVICE_CONTAINER_NAME", unset="")
IS_DEBUG <- Sys.getenv("DEBUG", unset=FALSE)

if (nchar(trim(APPINSIGHTS_INSTRUMENTATIONKEY)) == 0) {
  APPINSIGHTS_INSTRUMENTATIONKEY = NULL
}

log <- function(message, sev, taskId, additionalProperties){
  if (!is.null(APPINSIGHTS_INSTRUMENTATIONKEY)) {
    payload <- get_payload(message, sev, APPINSIGHTS_INSTRUMENTATIONKEY, taskId, additionalProperties)
    if (IS_DEBUG) {
        print(payload)
      }
    r = POST(APP_SVC_URL, body=payload)

    if (status_code(r) != 200){
      print(http_status(r))
    }
  }
}

log_debug <- function(message, taskId, additionalProperties){
  log(message, "Verbose", taskId, additionalProperties)
}

log_info <- function(message, taskId, additionalProperties){
  log(message, "Information", taskId, additionalProperties)
}

log_warn <- function(message, taskId, additionalProperties){
  log(message, "Warning", taskId, additionalProperties)
}

log_error <- function(message, taskId, additionalProperties){
  log(message, "Error", taskId, additionalProperties)
}

log_exception <- function(message, taskId, additionalProperties){
  log(message, "Critical", taskId, additionalProperties)
}
  
get_payload <- function(msg, sev, key, taskId, additionalProperties){
  messaged <- msg
  severityLeveld <- sev
  propertiesd <- get_properties(taskId)

  if(!missing(additionalProperties)) {
    propertiesd <- c(propertiesd, additionalProperties)
  }

  baseDatad <- list(message = messaged, severityLevel = severityLeveld, properties = propertiesd)

  baseTyped <- "MessageData"

  named <- "MessageData"
  timed <- as.POSIXlt(Sys.time(), "UTC", "%Y-%m-%dT%H:%M:%SZ")
  iKeyd <- key
  datad <- list(baseType = baseTyped, baseData = baseDatad)
  payload <- list(name = named, time = timed, iKey = iKeyd, data = datad)

  json_payload <- toJSON(payload, pretty = TRUE, auto_unbox = TRUE)
  return(json_payload)
}

get_properties <- function(taskId){
  props <- list()
  props[[ "task_id" ]] <- taskId
  props[[ "service_owner" ]] <- CONF_SERVICE_OWNER
  props[[ "service_cluster" ]] <- CONF_SERVICE_CLUSTER
  props[[ "service_model_name" ]] <- CONF_SERVICE_MODEL_NAME
  props[[ "service_model_framework" ]] <- CONF_SERVICE_MODEL_FRAMEWORK
  props[[ "service_model_framework_version" ]] <- CONF_SERVICE_MODEL_FRAMEOWRK_VERSION
  props[[ "service_model_version" ]] <- CONF_SERVICE_MODEL_VERSION
  props[[ "service_name" ]] <- CONF_SERVICE_NAME
  props[[ "service_version" ]] <- CONF_SERVICE_VERSION
  props[[ "service_container_version" ]] <- CONF_SERVICE_CONTAINER_VERSION
  props[[ "service_container_name" ]] <- CONF_SERVICE_CONTAINER_NAME

  return(props)
}