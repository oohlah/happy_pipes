import BlynkLib, os
from time import time, sleep
from datetime import datetime
from upload_cloudinary import upload_image
import json
from environment_sensors import led_green, led_red
from environment_camera import capture_photo
#import requests library for url encoding
import requests
import paho.mqtt.client as mqtt

# MQTT configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_BLYNK = "/orla/env/now"  

# Connect MQTT client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# Blynk authentication
BLYNK_AUTH= os.getenv("BLYNK_AUTH")
blynk = BlynkLib.Blynk(BLYNK_AUTH)

# Determine base folder where script is running - the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
STATE_PATH = os.path.join(BASE_DIR, "state", "environment.json") # safely join base with json file

# Reading every 30 seconds
INACTIVITY_TIMEOUT = 30 #tested at 60 seconds
blynk.last_activity = time()

FIRST_BELOW_ZERO_TS=None
IMAGE_INTERVAL=3600 #set to 1 hour but tested at 30 seconds

# v1 is switch to turn off after inactivity
@blynk.on("V1")
def handle_v1_write(value):
    button_value = value[0]
    blynk.last_activity = time()  
    print(f'Current button value: {button_value}')
    if button_value=="1":
       print(f"fake placeholder for now")  # placeholder for now, expand later

# Read environment stats from JSON file
def read_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        print("There was a problem accessing json data.")  
        # reset json to write
        with open(STATE_PATH, "w") as f:
            json.dump({}, f)
        return {}  # Return empty dict so code doesn't crash


# save new env_state with URL of image once taken
def save_image(image_url):
    env = read_state() or {}

   # keep existing image - stops rewriting to None
    env["image"] = image_url  # store image URL as string
    env["image_ts"] = int(time())
    env["image_iso"] = datetime.now().isoformat(timespec="seconds")

    with open(STATE_PATH, "w") as f:
        json.dump(env, f, indent=2)
        print("State saved:", env)

        # Publish to MQTT so Flask can subscribe
        client.publish(MQTT_TOPIC_BLYNK, json.dumps(env))
        print("MQTT published:", env)

image_sent = False  # track if image has been sent already      

# Function to send camera image via Blynk API
def send_image():
    global image_sent #image sent flag prevents images from being taken repeatedly

    # Only send once per event
    if image_sent:
        return

    try:
        # Capture photo locally
        image_path = capture_photo()
        # Upload to Cloudinary and get URL
        image_url_cloud = upload_image(image_path)
        # Save image URL to state JSON
        save_image(image_url_cloud)

        # Publish state via MQTT
        with open(STATE_PATH, 'r') as f:
            payload = json.load(f)
        client.publish(MQTT_TOPIC_BLYNK, json.dumps(payload))
        print("MQTT event published:", payload)

        # Send image URL to Blynk virtual pin V2
        response = requests.get(
            "https://blynk.cloud/external/api/update/property",
            params={
                "token": BLYNK_AUTH,
                "pin": "V2",
                "urls": image_url_cloud
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

# Main loop
if __name__ == "__main__":
    print("Blynk application started. Listening for events...")

    last_ts = 0  # track last JSON timestamp

    try:
        while True:
            env = read_state() 
            current_ts = env.get("ts",0)  # get current timestamp from JSON
            temp = env.get("temperature_c", 0.0)
            dew_point = env.get("dew_point_c", 0.0)

            #if new update has occured
            if current_ts != last_ts:
                last_ts = current_ts  # update last timestamp
                print(f"{env}")
                led_green()  # indicate green LED
                blynk.run()  # run Blynk process
                blynk.virtual_write(0, temp)  # write temperature to Blynk
                blynk.virtual_write(3, dew_point)  # write dew point to Blynk

                # Check for dew point warning
                if dew_point < 13:
                    blynk.log_event("warning_dew_point_event")
                print(f"Dew Point: {dew_point}")

                temp_now=time() #set temp_now to current time

                # Temperature warning
                print(f"Temperature: {temp}°C")
                if temp <= 0:
                
                    if FIRST_BELOW_ZERO_TS is None: #this only runs once - when temp_now is None
                        FIRST_BELOW_ZERO_TS=temp_now #log time of temp falling below zero
                        image_sent=False
                        print(f"Temperature has fallen below zero: {datetime.fromtimestamp(FIRST_BELOW_ZERO_TS)} ")
                        led_red()
                        blynk.log_event("warning_temp_event")
                        send_image()  # send camera image
                        image_sent=True
                    
                    #else if temp has fallen below zero already and current time - initial drop is >= interval
                    elif FIRST_BELOW_ZERO_TS is not None and temp_now - FIRST_BELOW_ZERO_TS >= IMAGE_INTERVAL:
                        FIRST_BELOW_ZERO_TS = temp_now #reset temp_now, triggered in another hour
                        image_sent=False #set to False
                        led_red()
                        blynk.log_event("warning_temp_event") #send another warning
                        send_image() #send another image
                        image_sent=True
                elif temp > 5:
                    FIRST_BELOW_ZERO_TS = None #is temp raises into a safe temp zone then FIRST_BELOW_ZERO resets to None

            now = time()
            if now - blynk.last_activity > INACTIVITY_TIMEOUT:
                print(f"No activity for {INACTIVITY_TIMEOUT} seconds. Exiting.")
                break
            sleep(2)
    except KeyboardInterrupt:
        print("Blynk application stopped.")
    finally:
        # Stop MQTT loop and disconnect
        client.loop_stop()
        client.disconnect()
        print("MQTT client disconnected.")
