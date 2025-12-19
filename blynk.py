import BlynkLib, os
from time import time, sleep

from upload_cloudinary import image_url

import json

from environment_sensors import led_green, led_red

#import requests library for url encoding
import requests


BLYNK_AUTH= os.getenv("BLYNK_AUTH")

blynk = BlynkLib.Blynk(BLYNK_AUTH)

#determine base folder where script is running - the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
STATE_PATH = os.path.join(BASE_DIR, "state", "environment.json") #safely join base with json file

#reading every 30
INACTIVITY_TIMEOUT = 30
blynk.last_activity = time()

#v1 is switch to turn off after inactivity
@blynk.on("V1")
def handle_v1_write(value):
    button_value = value[0]
    blynk.last_activity = time()  
    print(f'Current button value: {button_value}')
    if button_value=="1":
       print(f"fake placeholder for now") #sense.clear(255,255,255)
    #else:
        #sense.clear()


image_sent = False

#read environment stats from json file
def read_state():
            with open(STATE_PATH, "r") as f:
                return json.load(f)

#WANT TO ADD INTERVAL TIMING TO IMAGE BEING SENT - EVERY 30 MINS

def send_image():
    global image_sent

    # Only send once per event
    if image_sent:
        return

    try:

        image = image_url()
        
        response = requests.get(
            "https://blynk.cloud/external/api/update/property",
            params={
                "token": BLYNK_AUTH,
                "pin": "V2",
                "urls": image
            }
        )

        print(f"Status: {response.status_code}, response: {response.text}")

        if response.status_code == 200:
            image_sent = True
        else:
            print(f"Failed to send image. Will retry later")
            sleep(10)
            image_sent = False

    except requests.RequestException as e:
        print(f"Exception sending image: {e}")
        image_sent = False



if __name__ == "__main__":
    print("Blynk application started. Listening for events...")
    try:
        while True:
            env = read_state() 
            print(f"{env}")
            led_green()
            blynk.run() #run Blynk
            temp = env["temperature_c"]  #get temperature from state

            #read dew_point from json
            dew_point = env["dew_point_c"]  #store env.dew_point_c in dew_point
            blynk.virtual_write(3, dew_point) #write dew_point to Blynk

            #test to see when dew_point below 13 - HARDCODED FOR NOW
            if dew_point < 13:
                blynk.log_event("warning_dew_point_event")
                print(f"Dew Point: {dew_point}")

            blynk.virtual_write(0, temp) #write temperature
            print(f"Temperature: {temp}°C")
            if temp <= 0:
                led_red()
                blynk.log_event("warning_temp_event")
                send_image()
            

            now = time()
            if now - blynk.last_activity > INACTIVITY_TIMEOUT:
                print(f"No activity for {INACTIVITY_TIMEOUT} seconds. Exiting.")
                break
            sleep(10)
    except KeyboardInterrupt:
        print("Blynk application stopped.")
        
        
 