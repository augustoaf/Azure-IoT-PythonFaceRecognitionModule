#by Augusto

from picamera import PiCamera
from time import sleep

camera = PiCamera()
camera.rotation = 180

camera.start_preview()

sleep(3)
camera.capture('image.jpg')

#For video recording, use this between start and stop preview:
#camera.start_recording('/home/pi/Desktop/video.h264')
##sleep(3)
#camera.stop_recording()

camera.stop_preview()
