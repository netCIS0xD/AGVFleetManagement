"""
mqtt_client.py

This script sets up an MQTT client to connect to a broker, subscribe to specific topics, 
and handle incoming messages by processing JSON payloads and storing the data in the database.

JSON Message Format:
The MQTT messages are expected to have a JSON payload with the following format:
{
    "temperature": 200,  # Optional, float or integer value representing temperature
    "voltage": 33,       # Optional, float or integer value representing voltage
    "current": 0.75      # Optional, float or integer value representing current
}

- Any of the fields (temperature, voltage, current) may be present or absent.
- Null or missing values are handled appropriately in the code.
"""

import json
import paho.mqtt.client as mqtt
from .models import SensorReading, EnvData

# MQTT_BROKER = 'broker.hivemq.com' # 192.168.9.126
MQTT_BROKER = 'broker.emqx.io'
MQTT_PORT = 1883

# 0,1,2 are QoS level, 0 at most once, 1 at least once, 2 exactly once
MQTT_TOPICS = [("sensor/amrdata", 0), ("sensor/voltage", 0), ("sensor/current", 0),("jialin/plant/+/humidity", 0)]

def on_connect(client, userdata, flags, rc):
    print(f"mqtt client: Connected to Server with result code {rc}")
    client.subscribe(MQTT_TOPICS)

def on_message(client, userdata, msg):
    print("mqtt received a msg: ", msg)
    try:
        payload = json.loads(msg.payload.decode())
        print("              payload: ", msg.topic)

        print("              payload: ", payload)
        if msg.topic == "sensor/amrdata":
            dataTemp = payload.get("temperature")
            dataV = payload.get("voltage")
            dataI = payload.get("current")

            # Check which fields are present and create the record accordingly
            if dataTemp is not None and dataV is not None and dataI is not None:
                SensorReading.objects.create(temperature=dataTemp, voltage=dataV, current=dataI)
            elif dataTemp is not None and dataV is not None:
                SensorReading.objects.create(temperature=dataTemp, voltage=dataV)
            elif dataTemp is not None and dataI is not None:
                SensorReading.objects.create(temperature=dataTemp, current=dataI)
            elif dataV is not None and dataI is not None:
                SensorReading.objects.create(voltage=dataV, current=dataI)
            elif dataTemp is not None:
                SensorReading.objects.create(temperature=dataTemp)
            elif dataV is not None:
                SensorReading.objects.create(voltage=dataV)
            elif dataI is not None:
                SensorReading.objects.create(current=dataI)

            # temperature = payload.get("temperature")
            # SensorReading.objects.create(temperature=temperature)
            # voltage = payload.get("voltage")
            # SensorReading.objects.create(voltage=voltage)
        elif msg.topic == "sensor/voltage":
            voltage = payload.get("voltage")
            SensorReading.objects.create(voltage=voltage)
        elif msg.topic == "sensor/current":
            current = payload.get("current")
            SensorReading.objects.create(current=current)
        else:
            import re
            # to match the topic "jialin/plant/+/humidity":
            # Extract the AMR ID from the topic using regular expression
            pattern = r"jialin/plant/(.+)/humidity"
            match = re.match(pattern, msg.topic)
            if match:
                dataAMRID = match.group(1)
                dataTemp = payload.get("temperature")
                dataH = payload.get("humidity")
                EnvData.objects.create(humidity=dataH,AMRID=dataAMRID)
                SensorReading.objects.create(humidity=dataH,AMRID=dataAMRID, temperature=dataTemp)
                print("   creat a record in both SensorReading and EnvData tables: humidity=",dataH, "AMRID=",dataAMRID)
            else:            
                print("Invalid topic format")


    except Exception as e:
        print(f"Error: in mqtt on_message(): {e}")


client = mqtt.Client()
# Assign the callback function
client.on_connect = on_connect
client.on_message = on_message
print("  To commenct MQTT server", MQTT_BROKER,":", MQTT_PORT)
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the loop to receive messages
client.loop_start()




