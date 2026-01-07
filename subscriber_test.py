import paho.mqtt.client as mqtt
import json
import time

#MQTT configuration - subscriber
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC_UDP = "/orla/env/udp"

#MQTT CALLBACKS

def on_connect(client, userdata, flags, rc):
    print("MQTT connected with result code", rc)
    client.subscribe(MQTT_TOPIC_UDP)
    print("Subscribed to:", MQTT_TOPIC_UDP)


def on_message(client, userdata, msg):
    print("MQTT message on", msg.topic)
    payload_str = msg.payload.decode("utf-8")
    data = json.loads(payload_str)  
    data["ts"] = int(time.time())

    print(f"MQTT DATA:{data}")


# Main loop
if __name__ == "__main__":
    print("Testing UDP HERE...")


    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # BLOCKS and keeps listening
    client.loop_forever()
   
