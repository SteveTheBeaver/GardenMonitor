# GardenMonitor
This code is used on a Raspberry Pi to track temperature/humidity using a DHT22 and send hourly images from a webcam.

# Garden Temperature and Humidity Tracker with Webcam Integration

## Purpose
This project tracks the temperature and humidity in your garden using a **DHT22** sensor, and sends this data to **InitialState** for real-time monitoring. Additionally, it captures images from a connected webcam every hour and sends them to **PushBullet** for remote viewing. The system also features an LED indicator that reflects the current temperature status.

## Requirements
This project requires a Raspberry Pi with the following components:
- **DHT22 sensor** (for temperature and humidity)
- **Webcam** (for image capture)
- **PushBullet account** (for image notifications)
- **InitialState account** (for streaming temperature and humidity data)
- **GPIO pins** for controlling LEDs and the button to toggle monitoring

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/SteveTheBeaver/GardenMonitor.git
cd GardenMonitor
```

### 2. Install required libraries

Run the following bash commands to install the necessary dependencies:

```bash
sudo apt update
sudo apt install python3-pip
sudo apt install python3-opencv
sudo apt install python3-dev
sudo apt install python3-rpi.gpio
sudo apt install libpigpio-dev
pip3 install pushbullet.py
pip3 install ISStreamer
pip3 install adafruit-circuitpython-dht
```

More information on pigpiod: https://github.com/joan2937/pigpio/blob/master/util/readme.md

### 3. Hardware Setup

- **DHT22 Sensor**: Connect the DHT22 sensor to GPIO pin 17 on your Raspberry Pi.  
- **Webcam**: Plug in your USB webcam and test it using `v4l2-ctl --list-devices` to ensure it's properly detected.
- **LEDs**: Connect two LEDs to GPIO pins 21 (Green LED) and 20 (Yellow LED).
- **Button**: Connect a button to GPIO pin 6. This button will toggle the monitoring state.

### 4. Configure API Keys

You'll need to set up the following services:

- **PushBullet API Key**: Obtain your PushBullet API key from [PushBullet's developer site](https://www.pushbullet.com/#settings).
- **InitialState**: Sign up for InitialState and obtain your **bucket key** and **access key**.

Open the `tracker.py` file and replace the following placeholders with your respective API keys:

```python
PUSHBULLET_API_KEY = "your_pushbullet_api_key"
streamer = Streamer(
    bucket_name="TrackerInterface",
    bucket_key="your_bucket_key",  # Replace with your bucket key
    access_key="your_access_key"  # Replace with your access key
)
```

### 5. Running the Script

Ensure your main Python file is located in the same directory as the rest of the project files. Then, simply run the Python script with:

```bash
python3 main.py
```

The script will start by monitoring the temperature and humidity, and it will send hourly images from the webcam to PushBullet. Press the button connected to GPIO pin 6 to toggle the monitoring state.

### 6. Stopping the Script

You can stop the script by pressing `CTRL+C`. The script will perform any necessary cleanup, including GPIO pin resets and releasing camera resources.

## How It Works

- **Temperature and Humidity Monitoring**: The DHT22 sensor reads the temperature and humidity values. This data is sent to InitialState every 2 seconds for real-time tracking.
- **LED Indicator**: The Green LED indicates that monitoring is active. The Yellow LED lights up if the temperature goes above 85°F or below 50°F.
- **Image Capture**: Every hour, the system captures an image from the webcam and sends it via PushBullet. The image is also streamed to InitialState.

## Code Acknowledgements

- **DHT22 Code**: The code for reading the DHT22 sensor was adapted from [The Zan Show](https://thezanshow.com/electronics-tutorials/raspberry-pi/tutorial-26).
- **Friend Contributions**: A friend helped with certain aspects of hardware setup, debugging, and PushBullet/Webcam related stuff .
- **AI Assistance**: Some code segments were assisted by AI tools to bring everything together, as I tested components in separate Python files.

## License

This project is open-source. Feel free to modify to your needs!
