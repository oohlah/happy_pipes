from flask import Flask, request, render_template
from flask_cors import CORS
import os, json, datetime, time
import json
import paho.mqtt.client as mqtt
from chart import generate_chart

#importt thread for chart process
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

# static directory with jpg/png
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

def load_state():
    try:
        with open(STATE_PATH) as f:
            data = json.load(f)
        ts = data.get("ts")
        if not ts:
            return None
        age = int(time.time()) - ts
        time_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        data["age"] = age
        data["time_str"] = time_str
        return data
    except FileNotFoundError:
        return None
    except Exception as e:
        print("Error loading state:", e)
        return None
    
@app.route('/api/environment',methods=['GET'])
def current_environment():
    env = load_state()
    
    return {
        "temperature_c": env["temperature_c"],
        "humidity_percent": env["humidity_%"],
        "dew_point_c": env["dew_point_c"],
        "timestamp": env["iso"],
        "image": env.get("image"),
    }

@app.route('/') 
def index():
   env = load_state()
   fig = os.path.basename(CHART_PATH)

   return render_template("status.html", env=env, plot_data=fig)


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

#generate chart every 30 seconds without blocking flask
#chart responds to csv updates
def chart_loop():
    while True:
        try:
            generate_chart()
        except Exception as e:
            print("Chart generation error:", e)

        time.sleep(30)  
    
t = Thread(target=chart_loop, daemon=True)
t.start() 

#Run API on port 8000
app.run(host='0.0.0.0', port=8000) 

