# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
library(plumber)
r <- plumb("/app/my_api/api_example.R")
r$run(port=80, host="0.0.0.0")