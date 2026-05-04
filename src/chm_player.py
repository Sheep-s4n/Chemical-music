MUSIC_FILE_RELATIVE_PATH = "music_files/ashita.chm" 
# put your music file here, relative to the src folder
# than open a command line interface and run the command : python chm_player.py
# keep in mind that each reaction is different so the music might be faster or slower













from utils.oscillation_tracker import OscillationTracker
from utils.audio_engine import AudioEngine
from utils.plot_monitor import PlotMonitor
import time 

tracker = OscillationTracker(arduino_mode=False)
audio = AudioEngine(tracker, MUSIC_FILE_RELATIVE_PATH)
plotter = PlotMonitor(tracker)

tracker.start()
plotter.start()
audio.start()

while True :
    time.sleep(1)