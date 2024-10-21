# this file is the main file for the manual mission control
# it will be responsible for the following:
# running the manual mission control

# import the necessary libraries
import time
import paho.mqtt.client as mqtt # This ipythons the library to do the MQTT communications
import time # This is the library that will allow us to use the sleep function
import pygame
import sys

# define the runMission function
def manualMissionControl():
    print("Running manual mission control...")
    print("Starting mission in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("Manual Mission started!")

# function from Sophie's code



class KeyTypeError(Exception):
    def __init__(self):
        self.message = 'Key Recgonition Failed'
        super().__init__(self.message)

# The callback for when we connect to the server. The meaning of the return code (rc) can be found here:
# https://docs.oasis-open.org/mqtt/mqtt/v5.0/os/mqtt-v5.0-os.html#_Toc3901079
# A zero is good.
# After we connect we subsribe to one (or more) topics in this case the topic number 1
def on_connect(client,userdata,flags,rc):
    print ("Connected with result code "+str(rc))
    client.subscribe(MainTopic+"reply")


# The callback for when a PUBLISH message is received from the server. I.e. when a new value for the topic we subscribed to above updates
# the expression str(int(msg.payload.rstrip(b'\x00'))) converts the message from the server to an integer and then a string for printing.
# Specifically:
#   msg.payload.rstrip(b'\x00') This is getting all the bytes from the server (should be 11 in our case) and removes bytes with the value \x00 from the right
#   int() converts the remaining bytes into an integer, it threats them as a string
#   str() converts the integer into a string for the purpose of printing it. See below (l.56) for an alternative way to do this
def on_message(client, userdata, msg):
    print(str(time.time())+" In topic: "+msg.topic+" the value was "+ str(int(msg.payload.rstrip(b'\x00'))))
  

# This function writes the value to MQTT of the state of the key
# Also picks up an L inputted to clear the MQTT channels, or a C to stop the program
def write_key_state(keyname, state, keystates):
    
    # Want to ensure that only one command is written to MQTT at a time
    # Conditional statement to see if it's trying to write a KEYDOWN (aka state=1)
    # then if any other keys are currently with a state of 1 it will continue without writing to MQTT
    if (state == 1) and (any(value == 1 for value in keystates.values())):
        # If the code has made it to here, that means that it's trying to write a keydown when there is another key already in the keydown state
        # Dont want this function to do anything, so return here
        return

    #print('processing key')
    if keyname == pygame.K_w:
        key = 'w'
    elif keyname == pygame.K_a:
        key = 'a'
    elif keyname == pygame.K_s:
        key = 's'
    elif keyname == pygame.K_d:
        key= 'd'
    elif keyname == pygame.K_l:
        client.publish(MainTopic+'w', payload="", retain=True)
        client.publish(MainTopic+'a', payload="", retain=True)
        client.publish(MainTopic+'s', payload="", retain=True)
        client.publish(MainTopic+'d', payload="", retain=True)
        
    elif keyname == pygame.K_c:
        raise(KeyboardInterrupt)
    else:
        raise(KeyTypeError)
    
    control_keys[key] = state                   # update the local dictionary that contains the current state of all the keys 
    client.publish(MainTopic+key,str(state))    # publish the key state to MQTT
    #print(control_keys)

def clear_MQTT_channels(keys):
    for key in keys:
        client.publish(MainTopic+key, payload="", retain=True)

### Pygame window functions ###

# Draw a single rounded rectangle with text
def draw_key(screen, text, x, y, width, height, color):
    # Draw rounded rectangle
    pygame.draw.rect(screen, color, pygame.Rect(x, y, width, height), border_radius=10)
    # Render the key letter in the center
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=(x + width // 2, y + height // 2))
    screen.blit(label, label_rect)

# Update and render the key states
def render_keys(key_states):
    screen.fill((200, 200, 200))  # Clear screen with background color
    
    # Draw WASD keys with appropriate colors based on key state
    draw_key(screen, 'W', 160, 100, 80, 80, GREY if key_states['w'] else WHITE)
    draw_key(screen, 'A', 50, 200, 80, 80, GREY if key_states['a'] else WHITE)
    draw_key(screen, 'S', 160, 200, 80, 80, GREY if key_states['s'] else WHITE)
    draw_key(screen, 'D', 270, 200, 80, 80, GREY if key_states['d'] else WHITE)


### MAIN ###

# A dictionary to store the boolean state of w, a, s, and d regarding if they are being pressed or not
control_keys = {'w': 0,'a': 0,'s': 0,'d': 0,'l': 0,'c': 0}


# MQTT initialisation 
client = mqtt.Client()              # Create the mqtt client object
client.on_connect = on_connect      # Assign the function for the connection event
client.on_message = on_message      # Assign the function for the new message event

client.username_pw_set("student",password="HousekeepingGlintsStreetwise")  # Set the username and password
# Connect to the server using a specific port with a timeout delay (in seconds)
client.connect("fesv-mqtt.bath.ac.uk",31415,60)
# Create your main topic string. Everything else should be fields with values 1-8
MainTopic = "babyspice/directions/"
# Start the client to enable the above events to happen
client.loop_start()


# Initialize pygame
pygame.init()

# Set up screen
width = 400
height = width
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("BabySpice Manual Control Window")

# Define colors
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
BLACK = (0, 0, 0)

# Font for displaying text
font = pygame.font.Font(None, 60)

while(1):

    try:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt # send the code down to the part of the code that exits everything
            
            if event.type == pygame.KEYDOWN:
                write_key_state(event.key, 1, control_keys)
            
            if event.type == pygame.KEYUP:
                write_key_state(event.key, 0, control_keys)
        
        # Render the keys with updated states
        render_keys(control_keys)

        # Update display
        pygame.display.flip()
                

    except (KeyboardInterrupt):
        # Clear the MQTT channels
        clear_MQTT_channels(['w','a','s','d'])
        # Stop the Client
        client.loop_stop()
        # Disconnect
        client.disconnect()
        # Quit pygame
        pygame.quit()
        # Leave the while which will stop the code
        break

    except (KeyTypeError):
        continue

# run
if __name__ == "__main__":
    # This code will only run if this file is executed directly
    manualMissionControl()
