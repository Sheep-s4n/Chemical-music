# chemical_techno_realtime_fixed.py
from pyo import *
import numpy as np
import json
import random
import time

# ==============================
# Setup Pyo server
# ==============================
s = Server().boot()
s.start()

# ==============================
# MIDI → Hz conversion
# ==============================
def midi_to_hz(midi_note):
    return 440.0 * (2 ** ((midi_note - 69) / 12))

# ==============================
# Load chemical data
# ==============================
with open("valeurs_exp.json", "r") as f:
    raw_data = json.load(f)

data = np.array(raw_data, dtype=float)
data = (data - np.min(data)) / (np.max(data) - np.min(data))  # normalize 0 → 1

# ==============================
# Detect cycles (minima)
# ==============================
def detect_cycles(signal, threshold=0.1):
    cycles = []
    for i in range(1, len(signal)-1):
        if signal[i] < signal[i-1] and signal[i] < signal[i+1]:
            if (signal[i-1] - signal[i] > threshold) and (signal[i+1] - signal[i] > threshold):
                cycles.append(i)
    return cycles

smoothed = np.convolve(data, np.ones(5)/5, mode='same') # smothing data to reduce noise
cycle_indices = detect_cycles(smoothed, threshold=0.01)

print(len(cycle_indices))

# ==============================
# Phase computation
# ==============================
def compute_phase(index, cycles):
    for i in range(len(cycles)-1):
        if cycles[i] <= index < cycles[i+1]:
            return 2*np.pi * (index - cycles[i]) / (cycles[i+1] - cycles[i])
    return 2*np.pi

# ==============================
# Persistent global state
# ==============================
current_cycle = 0
next_cycle_index = cycle_indices[0]
bass_note = 40
filter_cutoff = 800
noise_amount = 0.1

# ==============================
# Persistent Pyo objects
# ==============================
# Kick
kick_env = Fader(fadein=0.001, fadeout=0.1, dur=0.1, mul=0.5)
kick_freq = Sig(50)
kick_osc = Sine(freq=kick_freq, mul=kick_env).out()

# Bass
bass_freq = Sig(midi_to_hz(bass_note))
bass_osc = Sine(freq=bass_freq, mul=0.3).out()

# Pad
pad_cutoff = Sig(filter_cutoff)
pad_osc = SuperSaw(freq=110, detune=0.5, bal=0.7, mul=0.2)
pad_filt = ButLP(pad_osc, freq=pad_cutoff).out()

# ==============================
# Real-time simulation loop
# ==============================
data_index = 0
while True:
    # Detect chemical clock tick
    trigger_kick = False
    if data_index >= next_cycle_index:
        trigger_kick = True
        # New variation each cycle
        bass_note = random.choice([40, 43, 45, 47])
        filter_cutoff = random.uniform(600, 1200)
        noise_amount = random.uniform(0.0, 0.3)
        current_cycle += 1
        if current_cycle < len(cycle_indices)-1:
            next_cycle_index = cycle_indices[current_cycle]

        # Trigger kick envelope
        kick_env.play()
        # Kick frequency sweep
        kick_freq.value = random.uniform(50, 80)

        # Update bass note frequency
        bass_freq.value = midi_to_hz(bass_note)

        # Update pad filter cutoff
        pad_cutoff.value = filter_cutoff

    # Compute phase for modulation
    phase = compute_phase(data_index, cycle_indices)

    # Bass modulation
    bass_osc.freq.value = float(midi_to_hz(bass_note) * (1 + 0.05*np.sin(phase)))

    # Pad filter modulation
    pad_cutoff.value = float(filter_cutoff * (0.5 + 0.5*np.sin(phase)))

    # Increment index
    data_index += 1
    if data_index >= len(data):
        data_index = 0  # loop for continuous play

    time.sleep(0.01)  # small delay to simulate real-time sensor