import time
import sounddevice as sd
import soundfile as sf
import numpy as np
import threading

from .led_controller import LEDController


class LightSoundController:

    # -------------------------
    # AUDIO REGISTRY
    # -------------------------
    AUDIO_FILES = {
        "ai_1": "../assets/sfx/AI_voice/AI_1_v2.mp3",
        "ai_2_fr": "../assets/sfx/AI_voice/AI_2_fr.mp3",
        "ai_3_fr": "../assets/sfx/AI_voice/AI_3_fr.mp3",
        "power_on": "../assets/sfx/LED/PowerOn_sfx.wav",
        "power_off": "../assets/sfx/LED/Poweroff_sfx.mp3",
        "ai_presentation" : "../assets/sfx/AI_voice/AI_presentation.wav"
    }
    
    MUSIC_FILE = "../assets/music/ambient/sci-fi_ambient.mp3"


    # -------------------------
    # INIT
    # -------------------------
    def __init__(self, port, baudrate=115200):

        self.leds = LEDController(port, baudrate)

        # audio cache: {name: (data, samplerate)}
        self.audio_cache = {}

        self._preload_audio()

        # warm up audio backend (reduces first-call latency)
        sd.play([0.0], 44100)
        sd.stop()
        
        # for background music
        self.music_volume = 0.25 # (ranging from 0 to 1) lower because it's ambient music, not the main focus
        self.music_thread = None
        self.music_running = False
        
        self.music_data, self.music_fs = sf.read(self.MUSIC_FILE)

    # -------------------------
    # PRELOAD SYSTEM
    # -------------------------

    def _preload_audio(self):
        for name, path in self.AUDIO_FILES.items():
            data, fs = sf.read(path)

            fade_ms = 50
            silence_ms = 100

            fade_samples = int(fs * fade_ms / 1000)
            silence_samples = int(fs * silence_ms / 1000)

            # apply fade-out
            if len(data) > fade_samples:
                fade_curve = np.linspace(1.0, 0.0, fade_samples)

                if data.ndim == 1:
                    data[-fade_samples:] *= fade_curve
                else:
                    data[-fade_samples:] *= fade_curve[:, None]

            # append silence
            if data.ndim == 1:
                silence = np.zeros(silence_samples)
            else:
                silence = np.zeros((silence_samples, data.shape[1]))

            data = np.concatenate([data, silence])

            self.audio_cache[name] = (data, fs)

    # -------------------------
    # AUDIO PLAYER
    # -------------------------
    def _play(self, name, blocking=True, pause_after=0.0):

        data, fs = self.audio_cache[name]

        if data.ndim == 1:
            data = np.column_stack([data, data])

        sd.play(data, fs)

        if blocking:
            sd.wait()
            if pause_after > 0:
                time.sleep(pause_after)

    # -------------------------
    # LIGHT UP SEQUENCE
    # -------------------------
    def light_up(self):

        self._play("ai_1", pause_after=0.5)
        self._play("ai_2_fr")

        # non-blocking LED sound
        self._play("power_on", blocking=False)

        time.sleep(0.7)
        self.leds.light_up()
        time.sleep(2) # to be sure the animation is fully finished

    # -------------------------
    # FADE OUT SEQUENCE
    # -------------------------
    def fade_out(self):

        self._play("ai_1", pause_after=0.5)
        self._play("ai_3_fr")

        self._play("power_off", blocking=False)

        time.sleep(0.7)
        self.leds.fade_out()

    def self_introduction(self):
        self.leds.breathing(14000)
        self._play("ai_presentation")
        
    
    def _music_loop(self):

        position = 0
        total = len(self.music_data)

        def callback(outdata, frames, time_info, status):

            nonlocal position

            if not self.music_running:
                outdata[:] = np.zeros((frames, 2))
                return

            end = position + frames

            # wrap-around loop
            if end > total:
                part1 = self.music_data[position:total]
                part2 = self.music_data[0:end - total]
                chunk = np.concatenate((part1, part2))
                position = end - total
            else:
                chunk = self.music_data[position:end]
                position = end

            # stereo safety
            if chunk.ndim == 1:
                chunk = np.column_stack([chunk, chunk])

            outdata[:] = chunk * self.music_volume

        with sd.OutputStream(
            samplerate=self.music_fs,
            channels=2,
            callback=callback,
        ):
            while self.music_running:
                time.sleep(0.1)
    
    def start_music(self):
        if self.music_running:
            return

        self.music_running = True
        self.music_thread = threading.Thread(target=self._music_loop, daemon=True)
        self.music_thread.start()
    
    def stop_music(self):
        self.music_running = False

        if self.music_thread:
            self.music_thread.join(timeout=1)
            self.music_thread = None
    # -------------------------
    # CLEANUP
    # -------------------------
    def close(self):
        self.leds.close()