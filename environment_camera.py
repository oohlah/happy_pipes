# import os allows you to interact with the underlying os

import time, os
from datetime import datetime

import json

from pi_camera_copy import Picamera2

from env_sensors2 import get_env_stats

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


picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (3280,2464)}))
picam2.start()
print("Camera started. Image will be taken once temperature drops")
STATE_DIR = os.path.join(BASE_DIR, "state")
os.makedirs(STATE_DIR, exist_ok=True)
STATE_PATH = os.path.join(STATE_DIR, "environment.json")

def capture_photo():
    print("Capturing Environment Image")
    picam2.capture_file(IMAGE_PATH) #capture file function stores image to path in argument
    time.sleep(0.3)
    print("Image Saved to: ", IMAGE_PATH)

def save_state(image_url=None):
    now = datetime.now()
    payload = {
        "environment": get_env_stats(),
        "image":image_url,# path to the image file
        "ts": int(now.timestamp()), 
        "iso": now.isoformat(timespec="seconds") 
    }
    with open(STATE_PATH, "w") as f:
        json.dump(payload, f)
    print("State saved:", payload)
    
    
try:
    while True:
            env = get_env_stats() #store python dictionary in env
            temp = env["temperature_c"] #pull temperature reading
            print("Temperature:", temp)
            
            save_state()

            if env["temperature_c"] < 26.5:
                capture_photo()
                url = upload_image(IMAGE_PATH)
                save_state(url)
                time.sleep(5) #Don't take another image for 30mins
            else:
                 time.sleep(5) #sleep for 30 and then check temp again
                 url = upload_image(IMAGE_PATH)
                 
except KeyboardInterrupt:
    print("Exiting")
finally:
    picam2.stop()


