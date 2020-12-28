#by Augusto

import datetime
from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180

camera.start_preview()

sleep(3)
current_date_and_time = datetime.datetime.now()
current_date_and_time_string = str(current_date_and_time)
extension = '.jpg'
path = '/home/pi/workspace/images/unknown/'
file_name = path + current_date_and_time_string + extension
camera.capture(file_name)

#For video recording, use this between start and stop preview:
#camera.start_recording('/home/pi/Desktop/video.h264')
##sleep(3)
#camera.stop_recording()

camera.stop_preview()

print('picture filename: ' + file_name)
