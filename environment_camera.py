# import os allows you to interact with the underlying os

import time, os
from datetime import datetime

from picamera2 import Picamera2


#use os to set up base and static folder 

#determine base folder where script is running - the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
#inside base_dir there will be a folder called "static"
STATIC_DIR = os.path.join(BASE_DIR, "static")
# Ensure the static directory exists; makedirs can create nested folders if needed
# exist_ok=True means do nothing if the folder already exists (no error)
os.makedirs(STATIC_DIR, exist_ok=True)
#set image path - to add image to static_dir folder
IMAGE_PATH = os.path.join(STATIC_DIR, "last_env_image.jpg")

picam2=None #camera doesn't start on boot


# initialise camera, capture photo and save to image_path when called
def capture_photo():
        try:
            picam2 = Picamera2()
            #size: HD camera resolution
            picam2.configure(picam2.create_still_configuration(main={"size": (1280,720)}))
            picam2.start()
            print("Camera started. Image will be taken once temperature drops")
            print("Capturing Environment Image")
            picam2.capture_file(IMAGE_PATH) 
            time.sleep(0.3)
            print("Image Saved to: ", IMAGE_PATH)
            picam2.stop()
            return IMAGE_PATH
        except Exception as e:  # catch any error
            print(f"Camera error: {e}")
            time.sleep(1)
        raise Exception("Failed to capture image")


