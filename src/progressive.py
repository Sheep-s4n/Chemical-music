import matplotlib.pyplot as plt
from collections import deque
import threading
import time
from datetime import datetime, timedelta
from utils.simul_arduino import RealDataSimulator
import sounddevice as sd
import soundfile as sf
import numpy as np
from statistics import mean
from visuals.clock_ui import ChemicalClockUI
import pygame

"""
bug quand on pause le program : en bougeant la fenêtre ! (décalle le temps)
"""
threshold = 400
count_required = 2  # number of consecutive values to confirm transition

above_count = 0
below_count = 0
state = None  # None / 'high' / 'low'

audio_position = 0
filter_state = 0.0

up_transition_times = []
periods = []
chemical_clock_period = None
chemical_clock_time = 0
phase_error = 0

x = 0  # declare once globally


# --- Settings ---
BUFFER_SIZE = 2000
SMOOTH_SIZE =  30

X_MIN = 100   # minimum value of the sensor we trust
X_MAX = 700   # maximum value of the sensor we trust

PERIOD_AVG_COUNT = 2 # number of UP transitions used for averaging

MASTER_GAIN = 1.4

def load_mono(path):
    audio, sr_local = sf.read(path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    return audio, sr_local

others_audio, sr = load_mono("../assets/music/progressive/follow_waves/other.mp3")
piano_sound, _ = load_mono("../assets/music/progressive/follow_waves/isolated/piano.wav")
drums_audio, _ = load_mono("../assets/music/progressive/follow_waves/isolated/drums_1.wav")
vocals_audio, _ = load_mono("../assets/music/progressive/follow_waves/isolated/vocals_1.wav")
bass_audio, _ = load_mono("../assets/music/progressive/follow_waves/isolated/bass_1.wav")

pulse_position = 0        # current playhead
pulse_active = False      # whether it’s playing

clock_in_initialisation = True

play_piano_next = True

active_voices = []

trigger_order = [
    others_audio,
    drums_audio,
    vocals_audio,
    bass_audio
]
""" 
{
    "audio": np.array,
    "pos": int
}
"""

next_trigger_index = 1 # not 0 because we play other.mp3 first
# Trigger base sound immediately
active_voices.append({
    "audio": others_audio,
    "pos": 0
})
    
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
sensor = RealDataSimulator("experimental_data/valeurs_simul.json", sample_interval=0.01)

# --- Sensor reading thread ---
def sensor_thread():
    while True:
        value = int(sensor.read())
        smoothed = smooth(value)
        data_buffer.append(smoothed)
        time.sleep(0.01)  # match sensor sample interval
        

threading.Thread(target=sensor_thread, daemon=True).start()

# --- Matplotlib plot thread ---
def plot_thread():
    plt.ion()
    fig, ax = plt.subplots()
    # move the window top right 
    fig.canvas.manager.window.wm_geometry("+1000+0") # to move to window top right
    line, = ax.plot([], [], lw=2, color='blue')
    ax.set_xlim(0, BUFFER_SIZE)
    ax.set_ylim(0, 2000)  # adjust or make dynamic

    while True:
        if len(data_buffer) > 1:
            line.set_data(range(len(data_buffer)), list(data_buffer))
            ax.set_xlim(0, BUFFER_SIZE)
            ax.set_ylim(min(data_buffer)-50, max(data_buffer)+50)  # dynamic scaling
            fig.canvas.draw()
            fig.canvas.flush_events()
        time.sleep(0.01)

def audio_callback(outdata, frames, time_info, status):
    global filter_state, x, active_voices

    current_x = x
    alpha = brightness_from_x(current_x)
    current_vol = volume_from_x(current_x)

    mix = np.zeros(frames)
    

    voices_to_remove = []

    for voice in active_voices:
        audio = voice["audio"]
        pos = voice["pos"]

        remaining = len(audio) - pos
        to_read = min(frames, remaining)

        mix[:to_read] += audio[pos:pos+to_read]

        voice["pos"] += to_read

        if voice["pos"] >= len(audio):
            voices_to_remove.append(voice)

    # Remove finished voices
    # Keep only unfinished voices (safe in callback)
    active_voices[:] = [
        voice for voice in active_voices
        if voice["pos"] < len(voice["audio"])
    ]

    # Apply brightness filter
    filtered = np.zeros_like(mix)
    for i in range(len(mix)):
        filter_state += alpha * (mix[i] - filter_state)
        filtered[i] = filter_state

    filtered *= current_vol * MASTER_GAIN
    filtered = np.clip(filtered, -1.0, 1.0)

    outdata[:] = filtered.reshape(-1, 1)

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

ui = ChemicalClockUI()


# --- Main loop ---
while True:

    ui.handle_events()
    value = int(sensor.read())

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
        
        now = time.time()
        up_transition_times.append(now)
           # If at least two transitions, compute period
           

        if len(up_transition_times) >= 2 and clock_in_initialisation :
            new_period = up_transition_times[-1] - up_transition_times[-2]
            periods.append(new_period)

            if len(periods) == PERIOD_AVG_COUNT: # stop recording periods and begin the real process
                clock_in_initialisation = False
                chemical_clock_time = now

            chemical_clock_period = mean(periods)
            
            print(f"Instant period: {new_period:.3f}s")
            print(f"Averaged period of reference ({len(periods)} samples): {chemical_clock_period:.3f}s")
        
            # --- RUNNING PHASE ---
        elif not clock_in_initialisation:
            # Advance clock deterministically
            chemical_clock_time += chemical_clock_period
            phase_error = now - chemical_clock_time
                    
            print(f"Phase error: {phase_error:.4f}s")
            print(f"Chemical clock advanced to: {chemical_clock_time:.3f}")
        
        if play_piano_next:
            # Play piano pulse
            active_voices.append({
                "audio": piano_sound,
                "pos": 0
            })
            play_piano_next = False
        else:
            # Add next progressive layer
            if next_trigger_index < len(trigger_order):
                active_voices.append({
                    "audio": trigger_order[next_trigger_index],
                    "pos": 0
                })
                next_trigger_index += 1
                play_piano_next = True
    
    # drawing the UI ! only after processing the data
    ui.update_background(x,X_MIN,X_MAX)
    if clock_in_initialisation : 
        ui.draw_init(periods,
                chemical_clock_period,
                PERIOD_AVG_COUNT,
                ) 
    else : 
        ui.draw_active(chemical_clock_time,
                chemical_clock_period,
                phase_error)
        
    ui.update()

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

    time.sleep(0.01)

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