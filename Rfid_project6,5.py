"""
---------------------------------------------------------
RFID-Based Authentication System with Relay Control
Created by: Jaydeep Gupta
For: "JG Projects" YouTube Channel
Description:
This script integrates an RFID reader, OLED display, relay module, 
and MySQL database to authenticate users based on RFID cards. 
Unauthorized access triggers a buzzer alarm, while authorized 
cards activate the relay to open a gate or door.

GitHub Repository:
Youtube video:https://youtu.be/Sv5qsHx23_U
---------------------------------------------------------
"""
import os
import subprocess
import time
import mysql.connector
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import sys

# Initialize RFID reader
reader = SimpleMFRC522()

# Initialize OLED display
i2c = busio.I2C(board.SCL, board.SDA)
oled_width = 128
oled_height = 64
oled = SSD1306_I2C(oled_width, oled_height, i2c)

# Set up GPIO for relay and buzzer
RELAY_PIN = 18  # Relay GPIO pin
BUZZER_PIN = 16  # Buzzer GPIO pin
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay off initially (HIGH = inactive for active-low relay)
GPIO.output(BUZZER_PIN, GPIO.LOW)  # Buzzer off initially

# Clear OLED display
oled.fill(0)
oled.show()

# Prepare a blank image for drawing
image = Image.new("1", (oled_width, oled_height))
draw = ImageDraw.Draw(image)
font = ImageFont.load_default()

def display_message(line1, line2=""):
    """Display a message on the OLED screen with text wrapping for long lines."""
    draw.rectangle((0, 0, oled_width, oled_height), outline=0, fill=0)  # Clear screen

    def wrap_text(text, max_width):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if draw.textsize(test_line, font=font)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    # Wrap and split the lines
    max_width = oled_width
    line_height = 16
    wrapped_lines = wrap_text(line1, max_width)

    # Add line2 if there's space
    if line2:
        wrapped_lines += wrap_text(line2, max_width)

    # Display the lines on the OLED
    y_offset = 0
    for line in wrapped_lines[:oled_height // line_height]:
        draw.text((0, y_offset), line, font=font, fill=255)
        y_offset += line_height

    oled.image(image)
    oled.show()

def check_wifi():
    """Check if Wi-Fi is connected by pinging a public server."""
    try:
        subprocess.check_call(["ping", "-c", "1", "-W", "1", "8.8.8.8"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False

def reconnect_wifi():
    """Attempt to reconnect to Wi-Fi."""
    display_message("Wi-Fi Disconnected", "Reconnecting...")
    print("Reconnecting to Wi-Fi...")
    subprocess.call(["sudo", "wpa_cli", "-i", "wlan0", "reconnect"])
    time.sleep(5)

def check_server():
    """Check if the database server is reachable."""
    try:
        conn = mysql.connector.connect(
            host="192.168.184.96",
            user="raspberrypi",
            password="your_password",
            database="turnstile_auth",
            connect_timeout=5  # 5-second timeout
        )
        conn.close()
        return True
    except mysql.connector.Error as e:
        print("Database error:", e)
        return False

def reconnect_server():
    """Attempt to reconnect to the database server."""
    display_message("Server Not Connected", "Reconnecting...")
    print("Reconnecting to the server...")
    time.sleep(5)
    return check_server()

def authenticate_uid(uid):
    """Check if the UID exists in the database."""
    try:
        conn = mysql.connector.connect(
            host="192.168.184.96",
            user="raspberrypi",
            password="your_password",
            database="turnstile_auth"
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE uid = %s", (uid,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result:
            name = result[2]
            print(f"Fetched name: '{name}'")
            return name
        else:
            print("User not found!")
            return None
    except mysql.connector.Error as e:
        print("Database error in `authenticate_uid`:", e)
        display_message("Server Error", "Retrying...")
        return None

def activate_relay(name):
    """Turn on the relay for 5 seconds and display a welcome message."""
    welcome_message1 = "Welcome,"
    welcome_message2 = name.strip()
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Turn relay on (active low)
    display_message(welcome_message1, welcome_message2)
    print(welcome_message1, welcome_message2)
    print("Relay ON")

    start_time = time.time()
    while time.time() - start_time < 5:
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
        time.sleep(0.2)

    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Turn relay off
    print("Relay OFF")

def activate_buzzer():
    """Activate the buzzer for unauthorized access."""
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    print("Buzzer ON")
    time.sleep(2)
    GPIO.output(BUZZER_PIN, GPIO.LOW)
    print("Buzzer OFF")

# Main loop
while True:
    if not check_wifi():
        reconnect_wifi()
        if not check_wifi():
            display_message("Wi-Fi Error", "Restarting...")
            os.execv(sys.executable, ['python3'] + sys.argv)  # Restart program

    if not check_server():
        while not reconnect_server():
            time.sleep(5)

    try:
        display_message("System Ready", "Waiting for Card")
        id, text = reader.read()
        print("ID: ", id)

        if not check_server():
            display_message("Server Error", "Retrying...")
            continue

        user = authenticate_uid(str(id))
        if user:
            activate_relay(user)
        else:
            display_message("Access Denied", "Unauthorized Card")
            print("Access Denied")
            activate_buzzer()
    except Exception as e:
        print("Error:", e)
