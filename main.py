import os
from twilio.rest import Client
import RPi.GPIO as GPIO
import time
import datetime

# Set mode to use GPIO pin numbers /home/abhinav/.local/bin
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

RED_LIGHT = 4
DOOR_SENSOR_PIN = 18

DOOR_OPEN = 0
DOOR_CLOSED = 1

# define Twilio credentials for sending SMS messages
twilio_account_sid = "AC5286daa8eeXXXXXXXXXXX9376a9364396a"
twilio_auth_token = "d1d99cb89d12d4a7XXXXXXXXXX8d9a91"

# Initialize Mouse trap door state
is_door_open = 0
mouse_trapped = False

time_mouse_trapped = time.localtime

# Set up door sensor pin
GPIO.setup(DOOR_SENSOR_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

# Set up the light pins.
GPIO.setup(RED_LIGHT, GPIO.OUT)

#Set it to off
GPIO.output(RED_LIGHT, False)

# logic loop to determine whether door is open or not, we need to be alerted only if the door is closed since it implies the mouse would be inside
while not mouse_trapped:
    is_door_open =  GPIO.input(DOOR_SENSOR_PIN)
    if (is_door_open == DOOR_OPEN ):
        print(f"door open {is_door_open}")
        GPIO.output(RED_LIGHT, False)
    elif (is_door_open == DOOR_CLOSED ):
        print(f"door closed {is_door_open}")
        GPIO.output(RED_LIGHT, True)
        mouse_trapped = True
        time_mouse_trapped = datetime.datetime.now()
    time.sleep(0.5)

# Now the mouse is trapped. Send SMS message to dad
time_message_sent = time.perf_counter()

send_message = True
activate_release_mouse_sequence = False
while (is_door_open == DOOR_CLOSED and activate_release_mouse_sequence == False):

    time_counter = time.perf_counter()

    is_door_open =  GPIO.input(DOOR_SENSOR_PIN)

    msg_sent_elapsed_time = time_counter - time_message_sent

    trap_elapsed_time = datetime.datetime.now() - time_mouse_trapped

    #send alert messages every 15 minutes
    if ( msg_sent_elapsed_time > 60*15):
        send_message = True

    # If mouse is not released for x hours, then activate door open sequence to release mouse
    if (trap_elapsed_time.seconds > 60*60*1 ):
        activate_release_mouse_sequence = True

    if (send_message == True):
        msg_client = Client(twilio_account_sid, twilio_auth_token)
        body_msg = f"Mouse trapped at {time_mouse_trapped.strftime('%m/%d/%Y %H:%M')}. Elapsed time is {trap_elapsed_time}. Please release ASAP"
        message = msg_client.messages \
                            .create(body=body_msg, from_="whatsapp:+14155238886", to="whatsapp:+18602597324")
        print(message.sid)
        send_message = False
        time_message_sent = time.perf_counter()

if (activate_release_mouse_sequence == True ):
        msg_client = Client(twilio_account_sid, twilio_auth_token)
        body_msg = f"Mouse release sequence activated. Mouse is released !"
        message = msg_client.messages \
                            .create(body=body_msg, from_="whatsapp:+14155238886", to="whatsapp:+18602597324")
        # activate motors to open door

GPIO.output(RED_LIGHT, False)
print("Finished processing")
### TODO
# - Handle motors to open the door
# - Release the mouse if no action taken for more than 6 hours
# - OPTIONAL : Allow extension of time or handle being able to send a message to disarm the system
# - EVEN MORE OPTIONAL : Use motion sensor to verify whether the trap closing was a false flag