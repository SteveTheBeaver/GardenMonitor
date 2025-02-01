#SteveTheBeaver on Github
#DHT22 code taken from https://thezanshow.com/electronics-tutorials/raspberry-pi/tutorial-26

import os
import time
import datetime
import cv2
import pushbullet
import RPi.GPIO as GPIO
import pigpio
import DHT22
from ISStreamer.Streamer import Streamer

# Pushbullet Configuration
PUSHBULLET_API_KEY = "api_key"
pb = pushbullet.Pushbullet(PUSHBULLET_API_KEY)

# Initial State Configuration
streamer = Streamer(
    bucket_name="TrackerInterface",
    bucket_key="bucket_key",  # Replace with your bucket key
    access_key="access_key"  # Replace with your access key
)

# GPIO Configuration
GPIO.setmode(GPIO.BCM)
LED_PIN_1 = 21  # Green LED
LED_PIN_2 = 20  # Yellow LED
BUTTON_PIN = 6  # Button to control monitoring

# Set up GPIO pins
GPIO.setup(LED_PIN_1, GPIO.OUT)
GPIO.setup(LED_PIN_2, GPIO.OUT)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Initialize pigpio and DHT22
pi = pigpio.pi()
dht22 = DHT22.sensor(pi, 17)  # DHT22 on GPIO 17

# Initialize camera
camera = cv2.VideoCapture(0)  # Use 0 for first USB camera

# Global state variables
monitoring_active = False
last_capture_time = 0
CAPTURE_INTERVAL = 3600  # Capture and send image every hour
IMAGE_DIR = "/home/SteveTheBeaver/images/"

def ensure_image_directory():
    """Ensure the image directory exists"""
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

def read_dht22():
    """Read temperature and humidity from DHT22 sensor"""
    try:
        dht22.trigger()
        time.sleep(0.2)
        humidity = float('%.2f' % dht22.humidity())
        temp_c = float('%.2f' % dht22.temperature())
        temp_f = temp_c * (9 / 5) + 32
        return humidity, temp_f
    except Exception as e:
        print(f"Error reading DHT22 sensor: {e}")
        return None, None

def capture_image():
    """Capture image from USB camera"""
    try:
        ensure_image_directory()
        
        # Generate a unique filename based on the current timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_path = f"{IMAGE_DIR}{timestamp}.jpg"
        
        # Capture image using OpenCV
        ret, frame = camera.read()
        if ret:
            cv2.imwrite(image_path, frame)
            return image_path
        else:
            print("Failed to capture image")
            return None
    except Exception as e:
        print(f"Error capturing image: {e}")
        return None

def send_image_via_pushbullet(image_path):
    """Send image via Pushbullet"""
    try:
        with open(image_path, "rb") as image_file:
            file_data = pb.upload_file(image_file, os.path.basename(image_path))
            pb.push_file(**file_data)
        print(f"Image sent with Pushbullet.")
    except Exception as e:
        print(f"Error sending image with Pushbullet: {e}")

def stream_image_to_initialstate(image_path):
    """Stream image to InitialState"""
    try:
        with open(image_path, 'rb') as image_file:
            streamer.log_object("Camera", image_file, "image/jpeg")
        print("Image streamed to InitialState successfully")
    except Exception as e:
        print(f"Error streaming image to InitialState: {e}")

def update_leds(temperature):
    """Update LED states based on temperature"""
    if temperature is None:
        # Turn both LEDs off if temperature reading failed
        GPIO.output(LED_PIN_1, GPIO.LOW)
        GPIO.output(LED_PIN_2, GPIO.LOW)
    else:
        # Green LED indicates monitoring is active
        GPIO.output(LED_PIN_1, GPIO.HIGH)
        
        # Yellow LED indicates temperature out of range
        if temperature > 85 or temperature < 50:
            GPIO.output(LED_PIN_2, GPIO.HIGH)
        else:
            GPIO.output(LED_PIN_2, GPIO.LOW)

def toggle_monitoring():
    """Toggle the monitoring state"""
    global monitoring_active
    monitoring_active = not monitoring_active
    if not monitoring_active:
        # Turn off both LEDs when monitoring is stopped
        GPIO.output(LED_PIN_1, GPIO.LOW)
        GPIO.output(LED_PIN_2, GPIO.LOW)
    print(f"Monitoring {'started' if monitoring_active else 'stopped'}")
    streamer.log("Monitoring Status", "Active" if monitoring_active else "Inactive")
    streamer.flush()

def main():
    global last_capture_time
    
    print("Starting temperature monitoring and notification system...")
    print("Press the button to start/stop monitoring")
    
    try:
        while True:
            # Check button press
            if GPIO.input(BUTTON_PIN) == GPIO.LOW:
                toggle_monitoring()
                time.sleep(0.5)  # Debounce delay
            
            if monitoring_active:
                # Read temperature and humidity
                humidity, temperature = read_dht22()
                
                if temperature is not None:
                    # Update LEDs based on temperature
                    update_leds(temperature)
                    
                    # Stream temperature and humidity data
                    streamer.log("Temperature (F)", f"{temperature:.1f}")
                    streamer.log("Humidity (%)", f"{humidity:.1f}")
                    
                    # Check if it's time to capture and send an image (hourly)
                    current_time = time.time()
                    if current_time - last_capture_time >= CAPTURE_INTERVAL:
                        image_path = capture_image()
                        
                        if image_path:
                            # Send via Pushbullet
                            send_image_via_pushbullet(image_path)
                            
                            # Stream to InitialState
                            stream_image_to_initialstate(image_path)
                            
                            last_capture_time = current_time
                    
                    streamer.flush()
                    print(f"Temperature: {temperature:.1f}°F, Humidity: {humidity:.1f}%")
                
            time.sleep(2)  # Main loop delay

    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        # Cleanup
        GPIO.cleanup()
        pi.stop()
        camera.release()
        streamer.close()

if __name__ == "__main__":
    main()
