## AI for Earth - specifying a different CUDA version
The AI for Earth team hosts CUDA 9.2 on the mcr.microsoft.com repository. You are welcome to build your own, in the following way.

1. Run docker build with a custom base image (cuda:9.0-runtime-ubuntu16.04):
```
docker build . -f base-py/Dockerfile --build-arg BASE_IMAGE=nvidia/cuda:9.0-runtime-ubuntu16.04 -t <your_registry>.azurecr.io/aiforearth/base-py-cuda-90:1.2
```
2. Push your base image to your registry.