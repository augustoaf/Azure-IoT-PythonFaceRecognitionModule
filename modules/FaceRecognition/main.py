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

known_images_path = '/home/pi/workspace/images/known'
unknown_images_path = '/home/pi/workspace/images/unknown'

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "App requires python 3.5.3+. Current version of Python: %s" % sys.version )
        
        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        # Define behavior for receiving an input message on input1
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
                except Exception as ex:
                    print ( "Unexpected error in main_listener(): %s" % ex)
                    time.sleep(5)

        #def: list files from a folder and return files array
        def list_files(input_path):
            list = [] 
            for path,dirs,files in os.walk(input_path):
                for filename in files:
                    list.append(path+'/'+filename)
            return list

        #def: load faces from image files and return faces array - input is an array of filenames (with relative path)
        def load_faces(input_filenames):
            #load image files
            images_loaded_list = []
            for image_filename in input_filenames:
                try: 
                    images_loaded_list.append(face_recognition.load_image_file(image_filename))
                except Exception as ex:
                    print("wasn't able to load image: " + image_filename)
                    print ( "Unexpected error in load_faces(): %s" % ex)

            #load faces from images loaded
            counter = -1
            faces_list = []
            for image_loaded in images_loaded_list:
                counter += 1
                try:
                    #assumption to have only one face in the image, so it is getting the first face using the first index [0]
                    faces_list.append(face_recognition.face_encodings(image_loaded)[0])
                except Exception as ex:
                    #TODO test exception
                    print("wasn't able to locate any faces in image: " + input_filenames[counter])
                    print ( "Unexpected error in load_faces(): %s" % ex)
            return faces_list

        #def: routine to recognize face and send result to iot hub 
        def recognizeFace():
            try:
                print ( "RUNNING RECOGNIZE FACE ROUTINE ...")

                #load faces
                known_images_filename_list = list_files(known_images_path)
                unknown_images_filename_list = list_files(unknown_images_path)

                print('KNOWN IMAGES FILENAME:')
                for known_image_filename in known_images_filename_list:
                    print(known_image_filename)
                print('UNKNOWN IMAGES FILENAME:')
                for unknown_image_filename in unknown_images_filename_list:
                    print(unknown_image_filename)

                known_faces_list = load_faces(known_images_filename_list)
                unknown_faces_list = load_faces(unknown_images_filename_list)

                #loop all unknown faces
                unknown_counter = -1
                for unknown_face in unknown_faces_list:
                    unknown_counter += 1
                    known_counter = -1
                    face_found = False

                    print('DETECTING FACE ' + unknown_images_filename_list[unknown_counter] + ' ...')
                    # get results is an array of True/False telling if the unknown face matched anyone in the known faces array
                    faces_result = face_recognition.compare_faces(known_faces_list, unknown_face)
                    #loop the results and check if the unknown face has a match
                    for result in faces_result:
                        known_counter += 1
                        if result:
                            print('UNKNOWN FACE HAS A MATCH: ' + known_images_filename_list[known_counter])
                            face_found = True
                            quit

                    if not(face_found):
                        print('!!!FACE NOT FOUND!!!')
            except Exception as ex:
                print ( "Unexpected error in recognizeFace(): %s" % ex )

        # Schedule task for C2D Listener and twin property
        listeners = asyncio.gather(input1_listener(module_client), twin_patch_listener(module_client))

        print ( "APP READY ")

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