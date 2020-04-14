## blob-mount-py example
This example demonstrates how to mount an Azure Blob as a local virtual file system. It utilizes [Azure Storage Fuse](https://github.com/Azure/azure-storage-fuse) to achieve this mounting.

### Running
1. To get started, you will need to [create a new Azure Blob Container](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-portal) with a file named `config.csv`. We recommend using [Azure Storage Explorer](https://azure.microsoft.com/en-us/features/storage-explorer/) to aid in storage upload/download.
2. From within the Azure Portal or within Azure Storage Explorer, copy your blob's storage key.
3. Modify the [blob_mount.json](./blob_mount.json) file as follows:
    - accountName: This is the name of your blob storage account.
    - accountKey: This is the key that you copied in step 2.
    - containerName: This is the name of the container that you created in step 1. It is the container that will be mapped, locally.
    - mappedDirectory: This is the local path where your container will be mounted.

    Note: You may map as many containers as you would like in this file. The blob mounter will mount all of them.
4. Build your container with: `docker build .`. The final output line will state `Successfully built <image_id>`.
5. Run your example: `docker run -p 1212:1212 --cap-add SYS_ADMIN --device /dev/fuse <image_id>`.
