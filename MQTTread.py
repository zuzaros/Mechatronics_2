# OLD VERSION
# def MQTTread(channel):
# 
#     import paho.mqtt.client as mqtt
#     
#     # MQTT Broker details
#     broker = "fesv-mqtt.bath.ac.uk"
#     port = 31415
#     username = "student"
#     password = "HousekeepingGlintsStreetwise"
#     topic = "babyspice/"
# 
#     # Create a new MQTT client instance
#     client = mqtt.Client()
# 
#     client.username_pw_set(username, password)
#     # Connect to the broker
#     client.connect(broker, port, 60)
# 
#     client.subscribe(topic+channel)
# 
#     # Start the client to enable the above events to happen
#     client.loop_forever()
# 
#     return msg.payload.decode()


#Test   
#print(MQTTread("test"))

def MQTTread(channel):
    import paho.mqtt.client as mqtt
    import time

    # MQTT Broker details
    client = mqtt.Client()
    broker = "fesv-mqtt.bath.ac.uk"
    port = 31415
    username = "student"
    password = "HousekeepingGlintsStreetwise"
    topic = "babyspice/"
    received_messages = {}

    # This is a different function call based on this: http://www.steves-internet-guide.com/mqtt-python-callbacks/
    def on_connect(client, userdata, flags, rc):
        #print ("Connected with result code "+str(rc))
        #subscribe to topic and channel
        client.subscribe(topic+channel)

    # The callback for when a PUBLISH message is received from the server.
    def on_message(client, userdata, msg):
        received_message = int(msg.payload.decode())
        received_messages[msg.topic] = received_message
        #print(f"Received message '{received_message}' on topic '{msg.topic}'")

    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set(username,password)
    client.connect(broker,port,60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface
    #client.loop_forever()

    # Start the client loop in a separate thread
    client.loop_start()
    time.sleep(10)  # Allow some time for messages to be received
    client.loop_stop()

    return received_messages.get(topic + channel, 2) #return message received from mqtt. return 2 if no message is received

#Test
#executing_value = MQTTread("test")

#print(executing_value)

#if int(executing_value) == 0:
#    print("Test passed")
#else:
#    print("Test failed")

