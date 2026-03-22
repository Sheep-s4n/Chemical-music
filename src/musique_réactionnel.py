import numpy as np
import sounddevice as sd
import soundfile as sf
import time
from utils.simul_arduino import RealDataSimulator

sensor = RealDataSimulator("experimental_data/valeurs_simul.json", sample_interval=0.01)

X_MIN = 100   # minimum value of the sensor we trust
X_MAX = 700   # maximum value of the sensor we trust



# ======================
# LOAD AUDIO
# ======================

filename = "music/Lane8_mixtapesh.wav"
audio, samplerate = sf.read(filename, dtype="float32")

# Convert stereo → mono (simpler)
if len(audio.shape) > 1:
    audio = np.mean(audio, axis=1)
    

# Normalize
audio /= np.max(np.abs(audio))

# ======================
# VARIABLE (100 → 650)
# ======================

x = 300


def volume_from_x(x):
    # Map X_MIN → X_MAX to 0.2 → 1.0
    return 0.2 + (x - X_MIN) / (X_MAX - X_MIN) * 0.8

def pan_from_x(x):
    # Map X_MIN → X_MAX to -1 → +1 (equal-power pan)
    pan = -1 + 2 * (x - X_MIN) / (X_MAX - X_MIN)
    return np.clip(pan, -1, 1)  # ensure math safety


def brightness_from_x(x):
    # α: 0.01 → 0.49 (very muffled → almost full brightness)
    return 0.01 + (x - X_MIN) / (X_MAX - X_MIN) * 0.48

# ======================
# STREAM ENGINE (ONLY VOLUME)
# ======================

position = 0
filter_state = 0.0  # for brightness filter

def callback(outdata, frames, time_info, status):
    global position, x, filter_state
    
    # Get volume and brightness from sensor
    vol = volume_from_x(x)
    alpha = brightness_from_x(x)

    # Extract the next chunk of audio
    chunk = audio[position:position+frames]
    
    # Loop if we reach the end
    if len(chunk) < frames:
        remaining = frames - len(chunk)
        chunk = np.concatenate([chunk, audio[:remaining]])
        position = remaining
    else:
        position += frames

    # ===== Brightness Filter =====
    # Simple one-pole low-pass filter
    filtered = np.zeros_like(chunk)
    for i in range(len(chunk)):
        if not np.isfinite(filter_state):
            filter_state = 0  # reset if NaN
        filter_state += alpha * (chunk[i] - filter_state)
        filtered[i] = filter_state

    # Apply volume
    outdata[:] = (filtered * vol).reshape(-1, 1)
    
    
# ======================
# START STREAM
# ======================

print("Playing... Ctrl+C to stop")

with sd.OutputStream(
    samplerate=samplerate,
    channels=1,
    callback=callback,
    blocksize=512
):
    while True:
        # Example: slowly move x (just for demo)
        x = int(sensor.read())
        print(x)
        time.sleep(0.01)


    """_summary_
    Layer 1 = cosmic field (brightness controlled by the sensor data)
    Layer 2 = pulse (that expands through time)
    Layer 3 = Subtle filter resonance (derivative of the sensor data )
    """
    
    """_summary_
    process to smooth the signal
    plot the signal in real time 
    """