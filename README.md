Module App in Python to Recognize Faces

There is a routine triggered by a specific input message received on module, that routine compare faces in "new images" against known images and send the results to IoT Hub. It can process more than one "new image" at once.

Assumptions: 
- The code is handling images with only one face. 
- The app must access the images folder in the host OS, so it is necessary to bind the folder to Docker container have access.
Set Docker create parameters as below. Tip: check/validate the parameter using docker inspect <container id>:
{
  "HostConfig": {
    "Binds": [
      "/home/pi/workspace/images/:/home/pi/workspace/images/"
    ]
  }
}
- The trigger to recognize faces is an input message from a downstream device with payload value = "newImage". The Edge Hub routes are:
"fromModuleToIoTHub": "FROM /messages/modules/FaceRecognition/outputs/* INTO $upstream"
"fromDownstreamDeviceToModule": "FROM /messages/* WHERE NOT IS_DEFINED($connectionModuleId) INTO BrokeredEndpoint("/modules/FaceRecognition/inputs/input1")"
- For any Python Module App to run on Azure IoT Edge, the Edge Gateway Hostname in /etc/iotedge/config.yaml must be set according the device hostname (lower case), so in the downstream device this info in the connection string must be exactly the same (tip: on downstream device may be necessary to configure the hosts file to map the IP Address).  


Requirements:
- azure-iot-device lib (it was set to get latest from major version 2 - currently using 2.4.0)
- face_recognition lib (it was set to get latest version - currently using 1.3.0) 
Note: install this lib following the Docker reference listed below.
- Python 3.5.3 or above
- dlib being used is 19.9 version
- iotedge version 1.0.10.2

TODO (improvements)
- Try use the most recent version of dlib
- The paths to known and unkown images are hardcoded, move this to environment variables (the bind must reflect it)
- When module start, there is an error in input1_listener method (although it is not impacting anything)
- move images processed to images/processed folder

Reference:
face_recognition page
https://pypi.org/project/face-recognition/
Docker example for face_recognition in Python
https://github.com/ageitgey/face_recognition/blob/master/Dockerfile
Send output message examples
https://docs.microsoft.com/en-us/python/api/azure-iot-device/azure.iot.device.iothubmoduleclient?view=azure-python#send-message-to-output-message--output-name-
https://github.com/Azure/azure-iot-sdk-python/blob/master/azure-iot-device/samples/async-edge-scenarios/send_message_to_output.py

Troubleshooting:
If a package could not be installed from wheels, install it from source or use "pip --no-binary" parameter (which looks like install from source as well and might work - not tested).
Example of error message: "Could not build wheels for <packageName> which use PEP 517 and cannot be installed directly".

by Augusto