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
        "ai_obey": "../assets/sfx/AI_voice/AI_obey.mp3",
        "ai_2_fr": "../assets/sfx/AI_voice/AI_2_fr.mp3",
        "ai_3_fr": "../assets/sfx/AI_voice/AI_3_fr.mp3",
        "power_on": "../assets/sfx/LED/PowerOn_sfx.wav",
        "power_off": "../assets/sfx/LED/Poweroff_sfx.mp3",
        "ai_presentation" : "../assets/sfx/AI_voice/AI_presentation.wav",
        "ai_start_loading" : "../assets/sfx/AI_voice/AI_start_loading.mp3",
        "ai_end_loading" : "../assets/sfx/AI_voice/AI_end_loading.mp3",
    }
    


    # -------------------------
    # INIT
    # -------------------------
    def __init__(self, port="COM5", baudrate=115200):

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
        self.music_file = "../assets/music/ambient/sci-fi_ambient.mp3"

        
        self.music_data, self.music_fs = sf.read(self.music_file)

    # -------------------------
    # PRELOAD SYSTEM
    # -------------------------

    def _preload_audio(self):
        for name, path in self.AUDIO_FILES.items():
            data, fs = sf.read(path)

            fade_ms = 50
            silence_ms = 100

            fade_samples = int(fs * fade_ms / 1000) # number of samples for the fade-out duration
            silence_samples = int(fs * silence_ms / 1000)  # converts time → number of samples (because audio works in samples at a fixed sample rate)

            # apply fade-out
            if len(data) > fade_samples:
                fade_curve = np.linspace(1.0, 0.0, fade_samples) # This creates a gradual sequence.

                if data.ndim == 1: #mono
                    # with numpy data[:] you are not “creating a new array”.You are creating a: view onto the same memory
                    data[-fade_samples:] *= fade_curve # data[-fade_samples:] selects the last fade_samples of the audio data, and *= applies the fade curve to those samples, creating a smooth fade-out effect.
                else: #stereo or more channels, apply the same fade curve to all channels
                    data[-fade_samples:] *= fade_curve[:, None]

            # append silence
            if data.ndim == 1:
                silence = np.zeros(silence_samples)
            else:
                silence = np.zeros((silence_samples, data.shape[1])) #data.shape[1] = 2

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
        self.leds.breathing(15000)
        self._play("ai_presentation")
    
    def briggs_rauscher(self, p):
        self.leds.briggs_rauscher(p)
    
    def flash_leds(self):
        self.leds.flash_leds()
    
    def start_loading_animation(self):
        # save current state
        self._saved_music_file = self.music_file
        self._saved_music_volume = self.music_volume
        self._saved_music_data = self.music_data
        self._saved_music_fs = self.music_fs

        # play voice animation:
        self._play("ai_obey", pause_after=0.5)
        self.leds.breathing(16000)
        self._play("ai_start_loading")
        
        # switch to loading music
        self.stop_music()

        self.music_file = "../assets/music/epic/epic_music.mp3"
        self.music_volume = 1.0
        self.music_data, self.music_fs = sf.read(self.music_file)


        
        
        self.start_music()

    def end_loading_animation(self):
        self.stop_music()
        self.leds.breathing(5500)
        self._play("ai_end_loading")

        # play voice animation here

        # restore previous state
        self.music_file = self._saved_music_file
        self.music_volume = self._saved_music_volume
        self.music_data = self._saved_music_data
        self.music_fs = self._saved_music_fs
        # usually at this state the audio_engine takes the control of sound so this one is not needed anymore 
        
        

    # only for background music
    def _music_loop(self):

        position = 0 # were we are in the audio
        total = len(self.music_data) # last position

        def callback(outdata, frames, time_info, status): # called by OutputStream, the system calls it for the next audio chunk it needs
            # outdata --> the buffer provided by the audio system to fill with the next chunk of audio samples to play
            # frames --> the number of audio samples the system wants for this chunk (e.g., 1024 samples)
            
            nonlocal position # use the variable from the closest enclosing function where the variable already exists (so here it's the var in _music_loop, not a new local var in callback)

            if not self.music_running:
                outdata[:] = np.zeros((frames, 2)) # fill output buffer with silence if we decide to mute the background music
                return

            end = position + frames # next chunk size

            # wrap-around loop if we get to the end of the audio data (so we can loop the music seamlessly)
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
                chunk = np.column_stack([chunk, chunk]) # converts mono to stereo by duplicating the mono channel into both left and right channels
            
            outdata[:] = chunk * self.music_volume #reduce amplitude for ambient music
            # outdata is a numpy array [:] is used to select the entire array
            # its a shared buffer owned by the audio engine.
            
            # with outdata = chunk
            # Python now points outdata to chunk
            # BUT the sound system still points to the original buffer
            # just like in C “changing the pointer name doesn’t do anything”

        with sd.OutputStream(
            samplerate=self.music_fs, # fs 
            channels=2,
            callback=callback,
        ):
            while self.music_running:
                time.sleep(0.1)
                # Inside OutputStream: audio runs in a separate real-time thread (C-level thread) callback is called independently
                # So: callback does NOT keep your Python thread alive
                # therefore this loop is keeping it alive

    
    def start_music(self):
        if self.music_running: return # Avoid duplicate threads.

        self.music_running = True
        self.music_thread = threading.Thread(target=self._music_loop, daemon=True)
        self.music_thread.start()
    
    def stop_music(self):
        while self.music_volume > 0:
            self.music_volume -= 0.05
            time.sleep(0.1)
        self.music_running = False

        if self.music_thread:
            self.music_thread.join(timeout=1) # Pause the current thread for at most 1 seconds while waiting for music_thread to terminate.
            self.music_thread = None
    # -------------------------
    # CLEANUP
    # -------------------------
    def close(self):
        self.leds.close()