import RPi.GPIO as GPIO
import time

import googlemaps

from datetime import datetime
import geopy.distance

from maps import *

GPIO.setwarnings(False)

from display import *
oled = OLED

GPIO.setmode(GPIO.BCM)

# Button pin mapping
btn1 = 20
btn2 = 21

GPIO.setup(btn1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(btn2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Connect to Google Maps API
gmaps = googlemaps.Client(key='')

def right_button_pressed():
    return GPIO.input(btn1) == GPIO.HIGH

def left_button_pressed():
    return GPIO.input(btn2) == GPIO.HIGH

def selections():
    '''
    Returns parameters used in Google API query.
    Asks user for their preferences.
    Displays on OLED.
    '''
    
    # Method
    oled.display(["Will you be:","","","< Walking","","","< Driving"])
    method = ""
    while method == "":
        if right_button_pressed():
            method = "walking"
        if left_button_pressed():
            method = "driving"
            
    # Duration
    oled.display(["Travel time:","","","< Less than 30 mins","","","< More than 30 mins"])
    max_duration = ""
    while max_duration == "":
        if right_button_pressed():
            max_duration = 30
        if left_button_pressed():
            max_duration = 45
            
    # Price
    oled.display(["Price:","","","< Anything","","","< Less than $25"])
    max_price = ""
    while max_price == "":
        if right_button_pressed():
            max_price = 4
        if left_button_pressed():
            max_price = 2
            
    # Rating
    oled.display(["Rating:","","","< Anything","","","< At least 4 stars"])
    min_rating = ""
    while min_rating == "":
        if right_button_pressed():
            min_rating = 1
        if left_button_pressed():
            min_rating = 4
            
    return (method, max_duration, max_price, min_rating)

def directions_cycle(directions):
    '''
    Cycles through all the steps in the directions.
    Direction needs to be manually changed with the buttons.
    Future implementation will involve using coordinates
    from the GPS to know when to automatically switch to the
    next direction.
    '''
    
    steps = len(directions)
    
    for step in range(steps):
        text = directions[str(step)]['instructions']  
        oled.display(text.split())
           
        while not right_button_pressed() or not left_button_pressed():
            pass 
    

while True:
    
    # Welcome screen on OLED
    oled.display(["Welcome to", "idk.go"])
    while not right_button_pressed() or not left_button_pressed():
        pass
    
    # Get user preferences
    method, max_duration, max_price, min_rating = selections()
    
    # Get information for restaurant that is of best match
    output = get_best_match(
        location = (-73.6909461, 45.5206364), # FROM GPS (manual for now)
        min_price = 1,
        max_price = max_price, # FROM selections()
        max_distance = 100, # Closer distance is prioritized by API. Returns top 20.
        method = method, # FROM selections()
        max_duration = max_duration, # FROM selections()
        min_rating = min_rating # FROM selections()
    )
    
    # Display restaurant selection
    oled.display(["Going to:", output['name'], "", "Duration:", output['duration_text'], "Press to start"])
    
    while not right_button_pressed() or not left_button_pressed():
        pass
    
    # Get dictionary of directions to the restaurant
    output_directions = get_directions(
        location = (-73.6909461, 45.5206364), # FROM GPS (manual for now)
        method = method, # FROM selections()
        end_location = output['location']
    )
    
    # Cycle through and display the directions
    directions_cycle(output_directions)
    
    # End screen
    oled.display(["Thank You", "for using", "idk.go"])
    
    exit()
