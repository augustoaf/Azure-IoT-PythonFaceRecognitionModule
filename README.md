Module App in Python to Recognize Faces

It has a routine being executed periodically and that routine compare faces in a new image against knonw images in a folder, 
then return the name of the face recognized (if any) and send info to iot hub.
It also has a routine to configure the routine periodicity.

Requirements:
A- azure-iot-device lib
B- face_recognition lib (see options B1 and B2)
B1- if installing the App in a Docker container, install dependencies following the Docker reference listed below.
B2- if installing not using a Docker container (e.g., a "face recognition" App directly in Raspberry IP), usually the steps below works:
apt-get update
apt-get --yes install libatlas-base-dev
pip3 install cmake
pip3 install dlib
pip3 install face_recognition

Reference:
face_recognition page
https://pypi.org/project/face-recognition/
Docker example for face_recognition in Python
https://github.com/ageitgey/face_recognition/blob/master/Dockerfile

Troubleshooting:
If a package could not be installed from wheels which install from binary packages, install it from source or use "pip --no-binary" parameter (which looks like install from source as well and might work - not tested).
Example of error message: "Could not build wheels for <packageName> which use PEP 517 and cannot be installed directly".

by Augusto