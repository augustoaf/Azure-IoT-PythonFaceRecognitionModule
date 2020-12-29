# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import json
import time
import os
import shutil
import sys
import asyncio
from six.moves import input
import threading
from azure.iot.device.aio import IoTHubModuleClient
import face_recognition

known_images_path = '/home/pi/workspace/images/known'
unknown_images_path = '/home/pi/workspace/images/unknown'
processed_images_path = '/home/pi/workspace/images/processed'

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
            while True:
                try:
                    input_message = await module_client.receive_message_on_input("input1")  # blocking call - instructions below are executed when message on input1 received
                    print ( "EXECUTION OF input1_listener")
                    message = input_message.data
                    message_text = message.decode('utf-8')
                    if message_text=='newImage':
                        await recognizeFace()
                except Exception as ex:
                    print ( "Unexpected error in input1_listener: %s" % ex )

        # twin_patch_listener is invoked when the module twin's desired properties are updated.
        async def twin_patch_listener(module_client):
            print ( "\n")
        
        # define main listener
        def main_listener():
            while True:
                try:
                    #print ('running main_listener every 60sec')
                    time.sleep(60)
                except Exception as ex:
                    print ( "Unexpected error in main_listener(): %s" % ex)
                    time.sleep(30)

        #def: list files from a folder and return files array
        def list_files(input_path):
            list = [] 
            for path,dirs,files in os.walk(input_path):
                for filename in files:
                    list.append(path+'/'+filename)
            return list

        #def: load faces from image files and return faces array - input is an array of filenames (with absolute path)
        def load_faces(input_filenames):
            #load image files
            counter = -1
            images_loaded_list = []

            #clone list in order to iterate the array, once the original list can have filenames removed if can't load an image
            tmp_input_filenames = input_filenames.copy()
            for image_filename in tmp_input_filenames:
                counter += 1
                try: 
                    images_loaded_list.append(face_recognition.load_image_file(image_filename))
                except Exception as ex:
                    print("wasn't able to load image: " + image_filename)
                    move_file_to_processed_folder(input_filenames[counter])
                    #print ("Unexpected error in load_faces(): %s" % ex)
                    #once the item was not appended to the array, remove its ocurrence from the input_filenames array in order to match
                    #the contents in faces_list array, otherwise the results will mismatch the index for matching faces
                    input_filenames.pop(counter)
                    #decrease the counter once the current item wasn't appended, otherwise the next pop won't work as expected
                    counter -= 1

            #load faces from images loaded
            counter = -1
            faces_list = []
            for image_loaded in images_loaded_list:
                counter += 1
                try:
                    #assumption to have only one face in the image, so it is getting the first face using the first index [0]
                    tmp_faces = face_recognition.face_encodings(image_loaded)
                    faces_list.append(tmp_faces[0])
                except Exception as ex:
                    print("wasn't able to locate any faces in image: " + input_filenames[counter])
                    move_file_to_processed_folder(input_filenames[counter])
                    #print ( "Unexpected error in load_faces(): %s" % ex)
                    #once the item was not appended to the array, remove its ocurrence from the input_filenames array in order to match
                    # the contents in faces_list array, otherwise the results will mismatch the index for matching faces
                    input_filenames.pop(counter)
                    #decrease the counter once the current item wasn't appended, otherwise the next pop won't work as expected
                    counter -= 1

            return faces_list

        #def: send message to output1 (message_body can be a string, json, etc)
        async def send_message(message_body):
            try:
                message = message_body
                await module_client.send_message_to_output(message, "output1")
            except Exception as ex:
                print ( "Unexpected error: %s " % ex )

        #def: routine to recognize face and send result to iot hub 
        async def recognizeFace():
            try:
                print ( "\n RUNNING RECOGNIZE FACE ROUTINE ... \n")

                #load faces
                known_images_filename_list = list_files(known_images_path)
                unknown_images_filename_list = list_files(unknown_images_path)

                print('KNOWN IMAGES FILENAME:')
                for known_image_filename in known_images_filename_list:
                    print(return_last_text_split(known_image_filename))
                print('UNKNOWN IMAGES FILENAME:')
                for unknown_image_filename in unknown_images_filename_list:
                    print(return_last_text_split(unknown_image_filename))
                print ( "\n")
                
                known_faces_list = load_faces(known_images_filename_list)
                unknown_faces_list = load_faces(unknown_images_filename_list)

                #loop all unknown faces
                unknown_counter = -1
                for unknown_face in unknown_faces_list:
                    unknown_counter += 1
                    known_counter = -1
                    face_found = False
                    unknown_filename = return_last_text_split(unknown_images_filename_list[unknown_counter])
                    unknown_filename_absolute_path = unknown_images_filename_list[unknown_counter]

                    print('DETECTING FACE ' + unknown_filename + ' ...')
                    # get results is an array of True/False telling if the unknown face matched anyone in the known faces array
                    faces_result = face_recognition.compare_faces(known_faces_list, unknown_face)
                    #loop the results and check if the unknown face has a match
                    for result in faces_result:
                        known_counter += 1
                        if result:
                            known_filename = return_last_text_split(known_images_filename_list[known_counter])
                            print('MATCH IS ' + known_filename)
                            face_found = True
                            #send message to output1 in order to route to iot hub
                            message_body = 'face found for ' + unknown_filename + '. Match is ' + known_filename
                            await send_message(message_body)
                            quit

                    if not(face_found):
                        print('*** FACE NOT FOUND ***')
                        #send message to output1 in order to route to iot hub
                        message_body = 'face not found for ' + unknown_filename
                        await send_message(message_body)
                    
                    move_file_to_processed_folder(unknown_filename_absolute_path)
                    print ( "\n")
                    
            except Exception as ex:
                print ( "Unexpected error in recognizeFace(): %s" % ex )

        def return_last_text_split(text):
            result = text
            try:
                separator = '/'
                text_split = text.split(separator)
                result = text_split[len(text_split)-1]
            except:
                result = text
            return result

        #source must be the filename with absolute path; passing the filename to destination will force overwrite if file already exists 
        def move_file_to_processed_folder(source):
            try:
                filename = return_last_text_split(source)
                destination = processed_images_path
                shutil.move(source, destination+'/'+filename)
            except Exception as ex:
                print ( "wasn't able to move the file to processed folder. Exception: %s" % ex)

        # Schedule task for input module listener and twin property
        asyncio.gather(input1_listener(module_client), twin_patch_listener(module_client))

        print ( "APP READY ")

        # execute main_listener in another thread
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, main_listener)

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    asyncio.run(main())