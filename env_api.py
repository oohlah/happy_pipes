from flask import Flask, request, render_template
from flask_cors import CORS
import os, json, time
from datetime import datetime
import json
import paho.mqtt.client as mqtt
from chart import generate_chart

#import thread for chart process
from threading import Thread
import time

#determine base folder where script is running - the absolute path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
os.chdir(BASE_DIR) #
#path to json file
STATE_PATH = "state/environment.json"
os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
#path to csv file
CSV_PATH = "processing_data/env_data.csv"
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

# static directory with png
STATIC_PATH = os.path.join(BASE_DIR, "static")
os.makedirs(STATIC_PATH, exist_ok=True)

# path to chart image
CHART_PATH = os.path.join(STATIC_PATH, "temp_and_dew_point.png")

#create Flask app instance and apply CORS
app = Flask(__name__)
CORS(app)

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_BLYNK = "/orla/env/now" 

# Read environment stats from JSON file
def read_state():
    try:
        with open(STATE_PATH, "r") as f:
            return json.load(f)
    except json.decoder.JSONDecodeError:
        print("There was a problem accessing json data.")  # debug info
        # Reset json to write
        with open(STATE_PATH, "w") as f:
            json.dump({}, f)
        return {}  # Return empty dict so code doesn't crash

# Save new env_state with URL of image once taken
def save_state(chart_url=None):
   env = read_state() or {}

   # always update chart
   if chart_url:
       env["chart"] = chart_url  # store image URL as string

   # Add/Update timestamps
   env["chart_ts"] = int(datetime.now().timestamp())
   env["chart_iso"] = datetime.now().isoformat(timespec="seconds")

   try:
       with open(STATE_PATH, "w") as f:
           json.dump(env, f, indent=2)
       print("State saved:", env)
   except Exception as e:
       print("Error saving state:", e)

       save_state(env)  # persist JSON state
    
@app.route('/api/environment',methods=['GET'])
def current_environment():
    env = read_state()
    
    return {
        "temperature_c": env["temperature_c"],
        "humidity_percent": env["humidity_%"],
        "dew_point_c": env["dew_point_c"],
        "timestamp": env["iso"],
        "image": env.get("image"),
        "image_iso": env.get("image_iso"),
        "image_ts": env.get("image_ts"),
        "chart": env.get("chart")
    }

@app.route('/') 
def index():
   env = read_state()


   return render_template("status.html", env=env) 


#MQTT CALLBACKS

def on_connect(client, userdata, flags, rc):
    print("MQTT connected with result code", rc)
    client.subscribe(MQTT_TOPIC_BLYNK)
    print("Subscribed to:", MQTT_TOPIC_BLYNK)


def on_message(client, userdata, msg):
    print("MQTT message on", msg.topic)
    payload_str = msg.payload.decode("utf-8")
    data = json.loads(payload_str)  
    data["ts"] = int(time.time())

    with open(STATE_PATH, "w") as f:
        json.dump(data, f)
    print("State updated:", data)
   
       
# Set up MQTT client
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
mqtt_client.loop_start()  # run MQTT network loop in background thread

#generate chart every 30 seconds without blocking flask with threading
#chart responds to csv updates
def chart_loop():
    while True:
        print(f"starting chart loop...")
        try:
            chart_url = generate_chart()
            print(f"chart generated")
            save_state(chart_url)
        except Exception as e:
            print("Chart generation error:", e)

        time.sleep(30)  
    
t = Thread(target=chart_loop, daemon=True)
t.start() 

#Run API on port 8000
app.run(host='0.0.0.0', port=8000) 

