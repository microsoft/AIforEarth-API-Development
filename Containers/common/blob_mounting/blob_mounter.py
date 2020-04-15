# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import json
import subprocess
import os, shutil
import sys

def execute_bash(bash_command):
    print("Executing command: " + str(bash_command))
    process = subprocess.Popen(bash_command, shell=True)
    output, error = process.communicate()
    print("output: " + str(output))
    print("error: " + str(error))

with open('/app/fuse/blob_mount.json') as f:
    try:
        blob_config = json.load(f)

        if not os.path.exists("/var/fuze_connections"):
            os.mkdir("/var/fuze_connections")

        i = 0
        for cfg in blob_config:
            i = i + 1
            fuse_cfg_file = "/var/fuze_connections/fuse_" + str(i) + ".cfg"
            fuse_file = open(fuse_cfg_file, "w") 
            fuse_file.write("accountName " + cfg["accountName"] + "\n")
            fuse_file.write("accountKey " + cfg["accountKey"] + "\n")
            fuse_file.write("containerName " + cfg["containerName"] + "\n")
            fuse_file.close()

            base_dir = os.path.basename(cfg["mappedDirectory"])
            resource_dir = "/mnt/resource/blobfusetmp/" + base_dir

            os.makedirs(resource_dir)
            os.chmod(fuse_cfg_file, 700)
            os.makedirs(cfg["mappedDirectory"])

            fuze_mount_cmd = "blobfuse " + cfg["mappedDirectory"] + " --tmp-path=" + resource_dir + " --config-file=" + fuse_cfg_file + " -o attr_timeout=240" + " -o entry_timeout=240" + " -o negative_timeout=120"
            execute_bash(fuze_mount_cmd)

    except:
        print("Unexpected error during blob mounting")
        raise