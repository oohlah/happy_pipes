from sensor_listener import SensorListener
import json, math, os, time
from json_to_csv import save_csv
import paho.mqtt.client as mqtt

#path to json file
STATE_PATH = "state/environment.json"
os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)

#path to csv file
CSV_PATH = "processing_data/env_data.csv"
os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

# MQTT configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_UDP = "/orla/env/udp"  

# Connect MQTT client
client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

env_state = {
    "temperature_c": None,
    "humidity_%": None,
    "dew_point_c": None,
    "last_update": None,
    "ts": None,
    "iso": None,
    "image": None,  # empty image on initialisation
    "chart": None
}   

#calculate dew point from temp & humidity
def get_dew_point(temp, humi):
    A, B = 17.27, 237.7
    alpha = ((A * temp) / (B + temp)) + math.log(humi / 100.0)
    return (B * alpha) / (A - alpha)

#save to environment.json
def save_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH, "r") as f:
            old = json.load(f)
        #preserve chart and image fields 
        env_state["image"] = old.get("image")  # keep current image 
        env_state["chart"] = old.get("chart") # keep current chart
    env_state["ts"] = int(time.time())
    env_state["iso"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime())
    with open(STATE_PATH, "w") as f:
        json.dump(env_state, f, indent=2)

#handle ncoming pkt data and update to json
def handle_data(data):
    try:
        payload = json.loads(data) #load json from pkt
    except json.JSONDecodeError:
        return
    device = payload.get("device_id") 
    updated = False #track updated value
    if device == "temp_sense_01":
        env_state["temperature_c"] = round(payload.get("temperature"), 2)
        updated = True
    elif device == "humi_sense_01":
        env_state["humidity_%"] = round(payload.get("humidity"), 2)
        updated = True
    if env_state["temperature_c"] is not None and env_state["humidity_%"] is not None:
        env_state["dew_point_c"] = round(get_dew_point(env_state["temperature_c"], env_state["humidity_%"]), 2)
        env_state["last_update"] = int(time.time())
    if updated:
        #save to json
        save_state()
        #
        save_csv(env_state)

        # Publish to MQTT 
        client.publish(MQTT_TOPIC_UDP, json.dumps(env_state))
        print("MQTT published:", env_state)

if __name__ == "__main__":
    listener = SensorListener(port=5000)
    listener.callback = handle_data
    listener.start()
    print("Listener Service started. Waiting for data...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        listener.stop()
        print("Listener Service stopped")
    finally:
        # Stop MQTT loop and disconnect
        client.loop_stop()
        client.disconnect()
        print("MQTT client disconnected.")