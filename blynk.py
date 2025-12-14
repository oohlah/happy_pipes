import BlynkLib, os
from time import time, sleep
from sense_hat import SenseHat

from environment_sensors import get_dew_point

from upload_cloudinary import image_url

#import requests library for url encoding
import requests

sense = SenseHat()
sense.clear()

BLYNK_AUTH= os.getenv("BLYNK_AUTH")

blynk = BlynkLib.Blynk(BLYNK_AUTH)


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
        sense.clear(255,255,255)
    else:
        sense.clear()


image_sent = False

#WANT TO ADD INTERVAL TIMING TO IMAGE BEING SENT - EVERY 30 MINS

#send image function
def send_image():
     global image_sent 
     temp = sense.get_temperature()
     if temp < 26.5 and not image_sent:
        image = image_url() #store image in url variable
        print(f"Sending image URL to Blynk: {image}")
        
        url = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH}&pin=V2&value={image}"

        #encode url using requests library -safely send special characters
        encoded_data = requests.models.RequestEncodingMixin._encode_params(url)
        print(encoded_data)
       
        try:
            response = requests.get(encoded_data) #send url as get request to Blynk
            image_sent = True #block images from being sent repeatedly
        except Exception as e:
            print(f"Failed to send image URL")
        

if __name__ == "__main__":
    print("Blynk application started. Listening for events...")
    try:
        while True:
            blynk.run() #run Blynk
            image = image_url() #store image in url variable
            temp = sense.get_temperature() #get temperature from sense_hat

            humidity = sense.get_humidity()
            dew_point = get_dew_point(temp, humidity)
            blynk.virtual_write(3, dew_point) #write dew_point to Blynk

            #test to see when dew_point below 16 - REMOVE LINE
            dew_point = 15
            if dew_point < 16:
                blynk.log_event("warning_dew_point_event")
                print(f"Dew Point: {dew_point}")

            blynk.virtual_write(0, temp) #write temperature
            print(f"Temperature: {temp}°C")
            if temp < 26.5:
                blynk.log_event("warning_temp_event")
                send_image()
            

            now = time()
            if now - blynk.last_activity > INACTIVITY_TIMEOUT:
                print(f"No activity for {INACTIVITY_TIMEOUT} seconds. Exiting.")
                break
            sleep(2)
    except KeyboardInterrupt:
        print("Blynk application stopped.")
