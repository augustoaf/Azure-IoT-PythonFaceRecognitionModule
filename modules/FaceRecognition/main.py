# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import json
import time
import os
import sys
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
import face_recognition

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        # Define behavior for receiving an input message on input1
        # Because this is a filter module, we forward this message to the "output1" queue.
        async def input1_listener(module_client):
            print ( "input1_listener")

        # twin_patch_listener is invoked when the module twin's desired properties are updated.
        async def twin_patch_listener(module_client):
            print ( "twin_patch_listener")
        
        # define main listener
        def main_listener():
            while True:
                try:
                    recognizeFace()
                    time.sleep(15)
                except:
                    print ( "expection in") 
                    time.sleep(5)

        # routine to recognize face (if any, a message is sent to iot hub)  
        def recognizeFace():
            try:
                print ( "recognize face routine")

                picture_of_me = face_recognition.load_image_file("images/augusto.png")
                my_face_encoding = face_recognition.face_encodings(picture_of_me)[0]

                # my_face_encoding now contains a universal 'encoding' of my facial features that can be compared to any other picture of a face!

                unknown_picture = face_recognition.load_image_file("images/augusto2.png")
                unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]

                # Now we can see the two face encodings are of the same person with `compare_faces`!

                results = face_recognition.compare_faces([my_face_encoding], unknown_face_encoding)

                if results[0] == True:
                    print("It's a picture of me!")
                else:
                    print("It's not a picture of me!")      
            except Exception as ex:
                print ( "Unexpected error in recognizeFace(): %s" % ex )

        # Schedule task for C2D Listener and twin property
        listeners = asyncio.gather(input1_listener(module_client), twin_patch_listener(module_client))

        print ( "The sample is now waiting for messages. ")

        # "get the current thread loop and execute method"
        loop = asyncio.get_event_loop()
        ##user_finished = loop.run_in_executor(None, main_listener)
        loop.run_in_executor(None, main_listener)

        # Wait for user to indicate they are done listening for messages
        ##await user_finished

        # Cancel listening
        ##listeners.cancel()

        # Finally, disconnect
        ##await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    ##loop = asyncio.get_event_loop()
    ##loop.run_until_complete(main())
    ##loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    asyncio.run(main())