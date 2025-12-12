# import os allows you to interact with the underlying os

import time, os
from datetime import datetime

from sense_hat import SenseHat
from picamera2 import Picamera2

from upload_cloudinary import upload_image

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

sense = SenseHat()
sense.clear(0,0,0)


picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration())
picam2.start()
print("Camera started. Image will be taken once temperature drops")

def capture_photo():
    print("Capturing Environment Image")
    picam2.capture_file(IMAGE_PATH) #capture file function stores image to path in argument
    time.sleep(0.3)
    sense.clear(0,0,0)
    print("Image Saved to: ", IMAGE_PATH)

try:
    while True:
        temp = sense.get_temperature()

        if temp < 26.5:
            print(f"Temperature: {temp} Celcius")
            capture_photo()
            url = upload_image(IMAGE_PATH)
            save_state(url)
            sense.clear(255,0,0)
            time.sleep(30)
        elif temp > 26.5:
            sense.clear(0,255,0)
            print(f"Tempertaure Regulated: {temp} Celcius")
            sense.clear(0,255,0)
            time.sleep(30)
except KeyboardInterrupt:
    print("Exiting")
finally:
    picam2.stop()
    sense.clear()