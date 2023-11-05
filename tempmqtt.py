from machine import Pin,SoftI2C
import time
from umqttsimple import MQTTClient
import ubinascii
import machine
import micropython
import network
from bmp280 import *
import gc
gc.collect()
last_message = 0
message_interval = 5
counter = 0

bus = SoftI2C(scl='P6_0', sda='P6_1', freq=100000)
bmp = BMP280(bus)

bmp.use_case(BMP280_CASE_INDOOR)

ssid = 'xxxxxxx'
password = 'xxxxxxxxxx'
mqtt_server = 'xxx.xxx.xxx.xxx'  #Replace with your MQTT Broker IP
mqtt_port = 1883
client_id = ubinascii.hexlify(machine.unique_id())
print(client_id)
topic_sub = b'homeassistant/office/temperature'
topic_pub = b'homeassistant/office/temperature'
user = b'homeassistant'
password1 = b'xxxxxxxxxxxxxxx'

station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

while station.isconnected() == False:
  pass

print('Connection successful')
print(station.ifconfig())


def sub_cb(topic, msg):
  print((topic, msg))
  if topic == b'notification' and msg == b'received':
    print('ESP received hello message')

def connect_and_subscribe():
  global client_id, mqtt_server, topic_sub
  client = MQTTClient(client_id, mqtt_server, mqtt_port, user, password1)
  client.set_callback(sub_cb)
  client.connect()
  client.subscribe(topic_sub)
  print('Connected to %s MQTT broker, subscribed to %s topic' % (mqtt_server, topic_sub))
  return client

def restart_and_reconnect():
  print('Failed to connect to MQTT broker. Reconnecting...')
  time.sleep(10)
  machine.reset()

try:
  client = connect_and_subscribe()
except OSError as e:
  restart_and_reconnect()

while True:
  try:
    client.check_msg()
    temperature=bmp.temperature
    if (time.time() - last_message) > message_interval:
      msg = str(temperature)
      client.publish(topic_pub, msg)
      last_message = time.time()
      counter += 1
  except OSError as e:
    restart_and_reconnect()

