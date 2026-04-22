import json
import numpy as np
import sounddevice as sd
import soundfile as sf


class AudioEngine:
    def __init__(self, tracker, config_path, x_min=0, x_max=700, master_gain=1.4):
        self.tracker = tracker
        self.config_path = config_path
        self.x_min = x_min
        self.x_max = x_max
        self.master_gain = master_gain

        self.filter_state = 0.0
        self.content_list = []
        self.active_voices = []

        self.sample_rate = None
        self.stream = None

        self._load_config()

    def _load_mono(self, path):
        audio, sr = sf.read(path)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        return audio.astype(np.float32), sr

    def _load_config(self):
        with open(self.config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        for item in config["content_list"]:
            audio, sr = self._load_mono(item["file"])

            if self.sample_rate is None:
                self.sample_rate = sr

            self.content_list.append({
                "audio": audio,
                "volume": item["volume"],
                "mode": item["mode"],
                "start_cycle": item["start_cycle"],
                "retrigger_rate": item.get("retrigger_rate", 1),
                "triggered": False,
                "pending_retriggers": 0,
                "last_cycle_seen": -1
            })

        for item in self.content_list:
            if item["mode"] == "sustain" and item["start_cycle"] == 0:
                self.active_voices.append({
                    "audio": item["audio"],
                    "pos": 0,
                    "volume": item["volume"],
                    "loop": True
                })

    def brightness_from_x(self, x):
        alpha_min = 0.01
        alpha_max = 0.25
        norm = (x - self.x_min) / (self.x_max - self.x_min)
        norm = max(0.0, min(1.0, norm))
        return alpha_min + norm * (alpha_max - alpha_min)

    def volume_from_x(self, x):
        norm = (x - self.x_min) / (self.x_max - self.x_min)
        norm = max(0.0, min(1.0, norm))
        return 0.55 - norm * 0.1

    def _trigger_cycle_sounds(self):
        cycle = self.tracker.cycle_count
        for item in self.content_list:
            mode = item["mode"]
            start_cycle = item["start_cycle"]

            if cycle < start_cycle:
                continue

            if mode == "add_once" and not item["triggered"]:
                self.active_voices.append({
                    "audio": item["audio"],
                    "pos": 0,
                    "volume": item["volume"],
                    "loop": False,
                    "source": item
                })
                item["triggered"] = True

            elif mode == "sustain" and not item["triggered"]:
                self.active_voices.append({
                    "audio": item["audio"],
                    "pos": 0,
                    "volume": item["volume"],
                    "loop": True,
                    "source": item
                })
                item["triggered"] = True

            elif mode == "retrigger":
                rate = item["retrigger_rate"]
                start_cycle = item["start_cycle"]

                # --- CASE 1: slow retrigger (rate < 1) ---
                if rate < 1:
                    interval = int(round(1 / rate))

                    if interval <= 0:
                        interval = 1

                    if (cycle - start_cycle) % interval == 0:
                        self.active_voices.append({
                            "audio": item["audio"],
                            "pos": 0,
                            "volume": item["volume"],
                            "loop": False,
                            "source": item
                        })

                # --- CASE 2: fast / multiple retriggers per cycle ---
                else:
                    # number of repeats per cycle
                    repeats = int(rate)

                    # avoid spamming every frame
                    if item["last_cycle_seen"] != cycle:
                        for _ in range(max(1, repeats)):
                            self.active_voices.append({
                                "audio": item["audio"],
                                "pos": 0,
                                "volume": item["volume"],
                                "loop": False,
                                "source": item
                            })

                        item["last_cycle_seen"] = cycle

    def _callback(self, outdata, frames, time_info, status):
        if self.tracker.just_went_up:
            self._trigger_cycle_sounds()
            self.tracker.just_went_up = False

        mix = np.zeros(frames, dtype=np.float32)

        for voice in self.active_voices[:]:
            audio = voice["audio"]
            pos = voice["pos"]
            volume = voice["volume"]

            remaining = len(audio) - pos
            to_read = min(frames, remaining)

            mix[:to_read] += audio[pos:pos+to_read] * volume
            voice["pos"] += to_read

            if voice["pos"] >= len(audio):
                if voice["loop"]:
                    voice["pos"] = 0
                else:
                    #self.active_voices = [v for v in self.active_voices if v is not voice]
                    source = voice.get("source")

                    self.active_voices = [v for v in self.active_voices if v is not voice]
                    if source and source["mode"] == "retrigger":
                        if source["pending_retriggers"] > 0:
                            source["pending_retriggers"] -= 1

                            self.active_voices.append({
                                "audio": source["audio"],
                                "pos": 0,
                                "volume": source["volume"],
                                "loop": False,
                                "source": source
                            })

        alpha = self.brightness_from_x(self.tracker.smoothed_value)
        sensor_volume = self.volume_from_x(self.tracker.smoothed_value)

        filtered = np.zeros_like(mix)

        for i in range(len(mix)):
            self.filter_state += alpha * (mix[i] - self.filter_state)
            filtered[i] = self.filter_state

        filtered *= sensor_volume * self.master_gain
        filtered = np.clip(filtered, -1.0, 1.0)

        outdata[:] = filtered.reshape(-1, 1)

    def start(self):
        self.stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=self._callback,
            blocksize=1024
        )
        self.stream.start()

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()