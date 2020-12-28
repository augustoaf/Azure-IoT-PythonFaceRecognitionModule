#by Augusto

import face_recognition
import os

known_images_path = '/home/pi/workspace/images/known'
unknown_images_path = '/home/pi/workspace/images/unknown'
unknown_image_filename = unknown_images_path + '/' + 'image.jpg'

#def: list files from a folder and return files array
def list_files(input_path):
	list = [] 
	for path,dirs,files in os.walk(input_path):
     		for filename in files:
        		list.append(path+'/'+filename)
	return list
#def: end

#def: load faces from image files and return faces array - input is an array of filenames (with relative path)
def load_faces(input_filenames):
	#load image files
	images_loaded_list = []
	for image_filename in input_filenames:
		try: 
			images_loaded_list.append(face_recognition.load_image_file(image_filename))
		except:
			print("wasn't able to load image: " + image_filename)

	#load faces from images loaded
	counter = -1
	faces_list = []
	for image_loaded in images_loaded_list:
		counter += 1
		try:
			#assumption to have only one face in the image, so it is getting the first face using the first index [0]
			faces_list.append(face_recognition.face_encodings(image_loaded)[0])
		except:
			#TODO test exception
			print("wasn't able to locate any faces in image: " + input_filenames[counter])
	return faces_list
#def: end

#load faces
known_images_filename_list = list_files(known_images_path)
unknown_images_filename_list = list_files(unknown_images_path)

for known_image_filename in known_images_filename_list:
  print(known_image_filename)

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

	print('************* detecting face ' + unknown_images_filename_list[unknown_counter] + ' ...')
	# get results is an array of True/False telling if the unknown face matched anyone in the known faces array
	faces_result = face_recognition.compare_faces(known_faces_list, unknown_face)
	#loop the results and check if the unknown face has a match
	for result in faces_result:
		known_counter += 1
		if result:
			print('************* unknown face has a match: ' + known_images_filename_list[known_counter])
			face_found = True
			quit

	if not(face_found):
        	print('************* face not found')

#print('known_faces_list: ' + str(len(known_faces_list)))
#print('known_images_loaded_list: ' + str(len(known_images_loaded_list)))
#print('known_images_filename_list: ' + str(len(known_images_filename_list)))

