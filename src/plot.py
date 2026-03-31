import matplotlib.pyplot as plt
from collections import deque
import threading
import time
from datetime import datetime, timedelta
from utils.simul_arduino import RealDataSimulator
import sounddevice as sd
import soundfile as sf
import numpy as np
import os 
import json 

# récolte de donner : auto
# adapter au l'arduino


import serial
import serial.tools.list_ports

# Getting opened ports :
serial_port = serial.tools.list_ports.comports()
value_list= []

for port in serial_port:
    print(f"{port.name} // {port.device} // D={port.description}")


PORT = "COM5"        # Windows : "COM3" / Linux : "/dev/ttyACM0"
BAUDRATE = 9600

ser = serial.Serial(PORT, BAUDRATE, timeout=1)

def init_experiment(directory="./experimental_data"):
    """
    Creates a new experiment file with the next index.
    Returns the file path.
    """
    os.makedirs(directory, exist_ok=True)

    # Find existing experiment indices
    indices = []
    for fname in os.listdir(directory):
        if fname.startswith("experiment_") and fname.endswith(".jsonl"):
            try:
                idx = int(fname.split("_")[1].split(".")[0])
                indices.append(idx)
            except (ValueError, IndexError):
                pass

    n = max(indices) + 1 if indices else 0
    file_path = os.path.join(directory, f"experiment_{n}.jsonl")

    # Create empty file
    open(file_path, "w").close()

    return file_path


def append_data(file_path, value, timestamp):
    """
    Append a JSON record: {"value": ..., "time": ...}
    """
    record = {"value": value, "time": timestamp}
    with open(file_path, "a") as f:
        json.dump(record, f)
        f.write("\n")

threshold = 400
count_required = 5  # number of consecutive values to confirm transition

above_count = 0
below_count = 0
state = None  # None / 'high' / 'low'

audio_position = 0
filter_state = 0.0

x = 0  # declare once globally


# --- Settings ---
BUFFER_SIZE = 2000
SMOOTH_SIZE =  30

X_MIN = 100   # minimum value of the sensor we trust
X_MAX = 700   # maximum value of the sensor we trust

MASTER_GAIN = 1.4

background_audio, sr = sf.read("../assets/music/ambient/soundscape_space_music_short.wav")

data_file = init_experiment()

if background_audio.ndim > 1:
    background_audio = background_audio.mean(axis=1)  # convert to mono
    
pulse_audio, pulse_sr = sf.read("../assets/music/pulse/far_hit.wav")
if pulse_audio.ndim > 1:
    pulse_audio = pulse_audio.mean(axis=1)  # convert to mono

pulse_position = 0        # current playhead
pulse_active = False      # whether it’s playing
pulse_length = len(pulse_audio)
    
#def brightness_from_x(x): # to play on if you want something more accurate
#    # α: 0.01 → 0.49 (very muffled → almost full brightness)
#   return 0.4 + (1.0 - 0.4)*(1 - (x - X_MIN)/(X_MAX - X_MIN))

def brightness_from_x(x):
    alpha_min = 0.01   # very deep
    alpha_max = 0.25   # brighter
    norm = (x - X_MIN) / (X_MAX - X_MIN)
    return alpha_min + norm * (alpha_max - alpha_min)
    
def volume_from_x(x):
    return 0.55 - (x - X_MIN) / (X_MAX - X_MIN) * 0.1





data_buffer = deque(maxlen=BUFFER_SIZE)
smooth_buffer = deque(maxlen=SMOOTH_SIZE)

first_blue_measured_time =0

def smooth(value):
    global x
    smooth_buffer.append(value)
    x= sum(smooth_buffer)/len(smooth_buffer)
    return x

# --- Initialize sensor ---
#sensor = RealDataSimulator("experimental_data/valeurs_simul.json", sample_interval=0.01)

# --- Sensor reading thread ---
def sensor_thread(): 
    while True :
        smoothed = smooth(x)
        data_buffer.append(smoothed)
        time.sleep(0.01)


threading.Thread(target=sensor_thread, daemon=True).start()

# --- Matplotlib plot thread ---
def plot_thread():
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], lw=2, color='blue')
    ax.set_xlim(0, BUFFER_SIZE)
    ax.set_ylim(0, 2000)  # adjust or make dynamic

    while True:
        if len(data_buffer) > 1:
            line.set_data(range(len(data_buffer)), list(data_buffer))
            ax.set_xlim(0, BUFFER_SIZE)
            #ax.set_ylim(min(data_buffer)-50, max(data_buffer)+50)  # dynamic scaling
            ax.set_ylim(100, 700) 
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(0.01)

def audio_callback(outdata, frames, time_info, status):
    global audio_position, filter_state, x
    global pulse_position, pulse_active

    # Get current sensor value safely
    current_x = x
    alpha = brightness_from_x(current_x)
    current_vol = volume_from_x(x)

    # Extract chunk from background (looping)
    chunk = background_audio[audio_position:audio_position+frames]

    if len(chunk) < frames:
        remaining = frames - len(chunk)
        chunk = np.concatenate([chunk, background_audio[:remaining]])
        audio_position = remaining
    else:
        audio_position += frames
        
    
    # Apply brightness filter (one-pole low-pass)
    filtered = np.zeros_like(chunk)
    for i in range(len(chunk)):
        filter_state += alpha * (chunk[i] - filter_state)
        filtered[i] = filter_state
    
    depth_factor = 1.0 + 0.2 * (1 - (current_x - X_MIN)/(X_MAX - X_MIN))
    filtered *= depth_factor
    
    # --- Pulse ---
    chunk_pulse = np.zeros(frames)
    if pulse_active:
        remaining = pulse_length - pulse_position
        to_read = min(frames, remaining)
        chunk_pulse[:to_read] = pulse_audio[pulse_position:pulse_position+to_read]
        pulse_position += to_read

        # Pulse finished?
        if pulse_position >= pulse_length:
            pulse_active = False
            pulse_position = 0

    # Apply brightness filter 
    
    bg = filtered * current_vol * MASTER_GAIN
    pulse = chunk_pulse * 0.4

    mix = bg*2 + pulse*0.5
    mix = np.clip(mix, -1.0, 1.0)

    outdata[:] = mix.reshape(-1, 1)
    #outdata[:] = (0.7*chunk_pulse + (filtered * (2*current_vol))).reshape(-1, 1)


# Start plotting in a daemon
threading.Thread(target=plot_thread, daemon=True).start()

# Start the reactive music
stream = sd.OutputStream(
    samplerate=sr,
    channels=1,
    callback=audio_callback,
    blocksize=1024
)

stream.start()


# --- Main loop ---
while True:

    
    try:
        line = ser.readline().decode('utf-8').strip()  # Read a line from serial
        if line:  # Make sure it's not empty
            value = int(line)  # Convert to int
            x = value
    except ValueError:
        # Skip lines that are not integers (sometimes Arduino sends empty lines)
        continue
    #value = int(ser.readline().decode("utf-8").strip()) #python Lit le port série jusqu’au caractère \n (qui définit la fin d'un bit)
    #value = int(sensor.read())
    print(value)
    
    append_data(data_file, value, timestamp=time.time())
    
    # Check for values above threshold
    if value > threshold:
        above_count += 1
        below_count = 0
    # Check for values below threshold
    elif value < threshold:
        below_count += 1
        above_count = 0
    else:
        # value in between thresholds
        above_count = 0
        below_count = 0

    # Detect transition to high
    if above_count >= count_required and state != 'high':
        print(f"Transition UP detected at value {value}")
        state = 'high'
        above_count = 0  # reset counter
        pulse_active = True  # <-- triggers the pulse
    """
        works like a charm : 
        if first_blue_measured_time == 0:
            first_blue_measured_time = datetime.now()
        else :
            delta = datetime.timestamp(datetime.now()) - datetime.timestamp(first_blue_measured_time)
            print("period : ",delta,"s")
            first_blue_measured_time = datetime.now()
    """

    # Detect transition to low
    if below_count >= count_required and state != 'low':
        print(f"Transition DOWN detected at value {value}")
        state = 'low'
        below_count = 0  # reset counter



""" 
with open("valeurs_simul.json", "r", encoding="utf-8") as f:
    data = json.load(f)

numbers = [int(x) for x in data]

step = 4
differences = [
    abs(numbers[i + step] - numbers[i]) if i % step == 0 else None
    for i in range(len(numbers) - step)
]
print(differences)

# un treshold à 90 devra bien fonctionner 
# plot with dots
plt.figure()
plt.scatter(range(len(differences)), differences)
plt.xlabel(f"Index (step = {step})")
plt.ylabel("Absolute difference")
plt.title(f"Absolute differences every {step} measurements")
plt.show()


"sound source:  The Ambient Luminary (YTB)"
"""