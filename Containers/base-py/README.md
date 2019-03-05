## Create a custom Python base image with a different CUDA version

The `base-py` image hosted by the AI for Earth team on the mcr.microsoft.com registry has CUDA 9.2 installed, so any images you create based on it will have this CUDA version. You are welcome to build your own base image with another version of CUDA, in the following way.

1. Navigate to `AIforEarth-API-Development/Containers` (one level above this directory).

2. Run `docker build` with a custom base image with your desired CUDA version. Specify this base image in the `BASE_IMAGE` argument (in this example, `nvidia/cuda:9.0-runtime-ubuntu16.04` is used as the base image):
```
docker build . -f base-py/Dockerfile --build-arg BASE_IMAGE=nvidia/cuda:9.0-runtime-ubuntu16.04 -t <your_registry>.azurecr.io/aiforearth/base-py-cuda-90:1.2
```

3. You can now specify the resulting image as your base image in your API's `Dockerfile`.

4. Push your base image to your registry so you can reuse it for other projects.
