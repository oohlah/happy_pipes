import BlynkLib, os
from time import time, sleep
from sense_hat import SenseHat

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

def send_image():
     global image_sent
     temp = sense.get_temperature()
     if temp < 26.5 and not image_sent:
        image = image_url() #store image in url variable
        print(f"Sending image URL to Blynk: {image}")
        
        url = f"https://blynk.cloud/external/api/update?token={BLYNK_AUTH}&pin=V2&value={image}"

        
        encoded_data = requests.models.RequestEncodingMixin._encode_params(url)
        print(encoded_data)
       
        try:
            response = requests.get(encoded_data)
            image_sent = True
        except Exception as e:
            print(f"Failed to send image URL")
        

if __name__ == "__main__":
    print("Blynk application started. Listening for events...")
    try:
        while True:
            blynk.run() #run Blynk
            image = image_url() #store image in url variable
            temp = sense.get_temperature() #get temperature from sense_hat
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
