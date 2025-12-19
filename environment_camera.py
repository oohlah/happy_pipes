# import os allows you to interact with the underlying os

import time, os
from datetime import datetime

import json

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


picam2 = Picamera2()
picam2.configure(picam2.create_still_configuration(main={"size": (3280,2464)}))
picam2.start()
print("Camera started. Image will be taken once temperature drops")
STATE_DIR = os.path.join(BASE_DIR, "state")
os.makedirs(STATE_DIR, exist_ok=True)
STATE_PATH = os.path.join(STATE_DIR, "environment.json")

#read json file with saved env_state
def read_env_state():
   try:
       with open(STATE_PATH, "r") as f:
           return json.load(f)
   except Exception:
       return None
   
def capture_photo():
    print("Capturing Environment Image")
    picam2.capture_file(IMAGE_PATH) #capture file function stores image to path in argument
    time.sleep(0.3)
    print("Image Saved to: ", IMAGE_PATH)

#save new env_state with url of image once taken
def save_state(image_url=None):
   env = read_env_state() or {}
   payload = env.copy()


   # Add/Update image info and timestamps
   payload["image"] = image_url
   payload["ts"] = int(datetime.now().timestamp())
   payload["iso"] = datetime.now().isoformat(timespec="seconds")


   try:
       with open(STATE_PATH, "w") as f:
           json.dump(payload, f, indent=2)
       print("State saved:", payload)
   except Exception as e:
       print("Error saving state:", e)
    
    
try:
    while True:
            #read current json file for env_state
            env = read_env_state()
            if env is None or "temperature_c" not in env:
                time.sleep(1)
                continue


            temp = env["temperature_c"]
            print("Temperature:", temp)


            save_state()  # Save latest environment stats without image change

            #if temp less than hardcoded for now
            if temp <= 0:
                capture_photo()
                url = upload_image(IMAGE_PATH)
                save_state(url)  # Save env stats + image URL
                time.sleep(10)  # Wait short time to test camera


            time.sleep(1)


except KeyboardInterrupt:
    print("Exiting")
finally:
    picam2.stop()


