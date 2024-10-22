def MQTTwrite(channel, number_to_send):
    import paho.mqtt.client as mqtt

    # MQTT Broker details
    broker = "fesv-mqtt.bath.ac.uk"
    port = 31415
    username = "student"
    password = "HousekeepingGlintsStreetwise"
    topic = "babyspice/"

    # Create a new MQTT client instance
    client = mqtt.Client()

    client.username_pw_set(username, password)
    # Connect to the broker
    client.connect(broker, port, 60)

    # Start the client to enable the above events to happen
    client.loop_start()

    # Publish the number to the specified topic
    client.publish(topic+channel, str(number_to_send))

    # Plot in the terminal what we just did
    print("%s %d" % (topic+channel, number_to_send))

    # Stop the Client
    client.loop_stop()
    
    # Disconnect from the broker
    client.disconnect()

#Test
#MQTTwrite("test", 10)