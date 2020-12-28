import os
start_path = '/home/pi/workspace/images/known'
#walk go through all folders inside the start_path as well
for path,dirs,files in os.walk(start_path):
     for filename in files:
        print (path+'/'+filename)
