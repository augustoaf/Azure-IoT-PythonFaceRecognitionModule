Module App in Python to Recognize Faces

There is a routine being executed periodically, that routine compare faces in new images against known images and return the result to iot hub. It can process more than one unknown images at once.

Assumptions: 
- The code are handling images with only one face. 
- The app must access the images folder in the host OS, so it is necessary to bind the folder to Docker container have access.
Set Docker create parameters as below. Tip: check/validate the parameter using docker inspect <container id>:
{
  "HostConfig": {
    "Binds": [
      "/home/pi/workspace/images/:/home/pi/workspace/images/"
    ]
  }
}

Requirements:
- azure-iot-device lib (it was set to get latest from major version 2 - currently using 2.4.0)
- face_recognition lib (it was set to get latest version - currently using 1.3.0) 
Note: install this lib following the Docker reference listed below.
- Python 3.5.3 or above
- dlib being used is 19.9 version
- iotedge version 1.0.10.2

TODO (improvements)
Try use the most recent version of dlib
The paths to known and unkown images are hardcoded, move this to environment variables (the bind must reflect it)
Configure the "face recognition routine" execution periodicity through twin properties

TODO (missing)
Send message (result from each unknonw image) to IoT Hub

#import 
from azure.iot.device.aio import IoTHubModuleClient, IoTHubMessage

#message constructor (message_body can be a string, json, etc/ topic)

def construct_message(message_body):
    try:
        msg_txt_formatted = message_body
        message = IoTHubMessage(msg_txt_formatted)

        # Add a custom application property to the message.
        # An IoT hub can filter on these properties without access to the message body.
        prop_map = message.properties()
        prop_map.add("source", "edgeGateway")

        # Send the message.
        print( "Sending message: %s" % message.get_string() )

    except IoTHubError as iothub_error:
        print ( "Unexpected error %s from IoTHub" % iothub_error )
        return

    return message

#send message to output
input_message = construct_message("payload")
await module_client.send_message_to_output(input_message, "output1")

reference: https://docs.microsoft.com/en-us/python/api/azure-iot-device/azure.iot.device.iothubmoduleclient?view=azure-python#send-message-to-output-message--output-name-

END TODO (missing)


Reference:
face_recognition page
https://pypi.org/project/face-recognition/
Docker example for face_recognition in Python
https://github.com/ageitgey/face_recognition/blob/master/Dockerfile

Troubleshooting:
If a package could not be installed from wheels, install it from source or use "pip --no-binary" parameter (which looks like install from source as well and might work - not tested).
Example of error message: "Could not build wheels for <packageName> which use PEP 517 and cannot be installed directly".

by Augusto