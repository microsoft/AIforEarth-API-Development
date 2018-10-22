# TensorFlow example

This example shows you how to deploy a TensorFlow model via an AI for Earth container. In this example we use an object detection model trained on the iNaturalist 2018 dataset.

In this example, the user will send an image to the API via a POST call. It is a long-running API, so a task ID will be returned when the endpoint is called. The API creates a SAS-keyed container within the API owner's Azure storage account. The SAS URL is returned to the caller via a status update.

## Download the model

You can download one of the two models trained on the iNaturalist dataset on the [Tensorflow detection model zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md), in section _iNaturalist Species-trained models_. Download the resnet50 model (smaller) instead of resnet101 to have fewer memory usage issues during testing. The file is about 0.5 GB in size. After you download and unzip the folder, find `frozen_inference_graph.pb` and move this file to directory `tf_iNat_api` at the current directory.

In this example, we copy the entire directory `tf_iNat_api` to the Docker container (see the `COPY` commands in `Dockerfile`), but there are other ways of accessing a model, such as placing it in a Azure blob storage container (a unit of blob storage, do not confuse with Docker _containers_) and mount that blob container.

## Modify Dockerfile

The `Dockerfile` in this example is a modified version of `base-py/Dockerfile`. The only modification is the additional commands to install TensorFlow and Pillow packages.


## Modify `supervisord.conf`
If you changed the name of the destination folder in the Dockerfile where your API folder is copied to (here we used `/api/tf_iNat_api/`), remember to modify two places in `supervisord.conf` that uses the location of the API folder.


## Download some sample images
You can download sample images from the iNat 2018 dataset from this [site](https://docs.google.com/spreadsheets/d/1JHn6J_9HBYyN5kaVrH1qcc3VMyxOsV2II8BvSwufM54).


## Example service

This example API endpoint takes an input image, performs object detection on it, renders the bounding boxes on the image (only if the confidence of the detected box is above 0.5, which is the `confidence_threshold` you can change in `tf_iNat_api/runserver.py`) and returns the annotated image. This is to demonstrate how to handle image input and output. Realistically you would probably return the coordinates of the bounding boxes and predicted categories in a json, rather than the rendered image.

Build the docker image (need to be in the Examples/tensorflow directory where the `Dockerfile` is):
```
docker build . -t tensorflow_example:1
```

Run image locally:
```
docker run --env-file=service_settings.env -p 8081:80 "tensorflow_example:1"
```

The argument `env-file` specifies the file that contains the necessary environment variables to be set inside the container when it starts. For this async API example, we saved the resulting imgae from the long running process to  blob storage. You need to create a storage account with Blob Storage, and assign the storage account name and the key (secondary) to `STORAGE_ACCOUNT_NAME` and `STORAGE_ACCOUNT_KEY` on the last two lines of `service_settings.env` in the current directory.

Run an instance of this image interactively and start bash to debug:
```
docker run -it tensorflow_example:1 /bin/bash
```


## Testing and calling the service

Testing locally, the end point would be at

```
http://localhost:8081/v1/tf_iNat_api/detect
```

You can use a tool like Postman to test the end point:

![Calling the async API](../screenshots/postman_tf_async_api.png)

In the _Body_ tab of Postman where you specify the body data to go with the POST request, you can upload the image you'd like to detect animals on as binary data under the _binary_ option. You also need to set the content type of the binary file to "image/jpeg" in the Headers tab, as follows:


![Calling the async API](../screenshots/postman_header_content_type.png)


You can see the output image with the detection bounding boxes labeled saved to your blob storage using Azure Storage Explorer (screenshot below) if you own or have access to that storage account, or you can download it using the SAS URL that was returned to the caller via another status update call.

![Calling the async API](../screenshots/storage_explorer_tf_out.png)

