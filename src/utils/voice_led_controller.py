import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

class VoiceLEDController:

    def __init__(self, model_path, sample_rate=16000):

        self.sample_rate = sample_rate

        self.q = queue.Queue(maxsize=3)

        self.model = Model(model_path)
        self.rec = KaldiRecognizer(self.model, sample_rate)

        self.latest_text = ""
        self.latest_command = None
        self.trigger_detected = False
        self.command_locked = False

        
        self.TRIGGERS = {"anthony", "anto", "en tout" , "tony"}

        self.LIGHT_ON = {
            "allumer", "allume", "active", "mettre", "démarre", "lance", "ouvre"
        }

        self.LIGHT_OFF = {
            "éteindre", "éteins", "éteint", "coupe", "désactive", "arrête", "fermer", "couper"
        }

        self.LIGHT_CONTEXT = {
            "lumière", "lumières", "l'éclairage", "éclairages",
            "lampe", "lampes", "spot", "spots",
            "éclairer", "allumage"
        }
        self.INTRO_VERBS = {
            "présente", "présenter", "présentes", "présentation",
            "décris", "décrire"
        }
        self.INTRO_PRONOUNS = {
            "toi", "toi-même", "vous", "tu", "te", "ta"
        }
        
        self.IDENTITY_WORDS = {
            "qui", "es", "identité"
        }
        
        self.START_WORDS = {
            "lance", "démarre", "demarre", "commence",
            "initialise", "active"
        }
        
        self.ANALYSIS_CONTEXT = {
            "analyse", "analyser",
            "cycle", "cycles",
            "mesure", "mesurer",
            "suivi", "observation"
        }
    # -------------------------
    # AUDIO CALLBACK
    # -------------------------
    def _callback(self, indata, frames, time, status):
        try:
            self.q.put_nowait(bytes(indata))
        except queue.Full:
            pass  # silently drop if not consumed yet

    # -------------------------
    # INTERNAL PARSER
    # -------------------------
    def _parse(self, text: str):
        if self.command_locked : return # don't parse new commands until current one is handled
        
        words = text.lower().split()
        print(words)
        trigger = any(w in self.TRIGGERS for w in words)
        if trigger or  "en tout" in text.lower():
            self.trigger_detected = True
        else:
            self.trigger_detected = False

        # 1. check if sentence is about light
        is_light_related = any(
            w in self.LIGHT_CONTEXT for w in words
        )

        if  is_light_related:

            # 2. detect ON intent
            if any(w in self.LIGHT_ON for w in words):
                self.latest_command = "LIGHT_ON"
                return

            # 3. detect OFF intent
            if any(w in self.LIGHT_OFF for w in words):
                self.latest_command = "LIGHT_OFF"
                return
        else : 
            # 4. detect self-introduction intent
            intro_requested = (
                any(w in self.INTRO_VERBS for w in words) and
                any(w in self.INTRO_PRONOUNS for w in words)
            )
            identity_requested = (
                "qui" in words and "es-tu" in words
            )

            if self.trigger_detected and (intro_requested or identity_requested):
                self.latest_command = "SELF_INTRODUCTION"
                return
            
            start_requested = any(w in self.START_WORDS for w in words)
            analysis_requested = any(w in self.ANALYSIS_CONTEXT for w in words)

            if self.trigger_detected and start_requested and analysis_requested:
                self.latest_command = "START_LOADING"
                return

        self.latest_command = None

    # -------------------------
    # PUBLIC UPDATE LOOP STEP
    # -------------------------
    def update(self):
        data = None

        try:
            data = self.q.get_nowait()
        except queue.Empty:
            return

        # always feed audio
        is_final = self.rec.AcceptWaveform(data)

        # ---- PARTIAL (fast) ----
        partial_result = json.loads(self.rec.PartialResult())
        partial_text = partial_result.get("partial", "")
        if partial_text:
            self.latest_text = partial_text
            self._parse(partial_text)

        
        # ---- FINAL (stable) ----
        if is_final:
            final_result = json.loads(self.rec.Result())
            final_text = final_result.get("text", "")
            self.latest_text = final_text
            self._parse(final_text)
            self.command_locked = False


    # -------------------------
    # QUERY METHODS
    # -------------------------
    def heard_trigger(self):
        return self.trigger_detected

    def get_command(self):
        return self.latest_command

    # -------------------------
    # STREAM START
    # -------------------------
    def start(self):

        self.stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=1024,
            dtype='int16',
            channels=1,
            callback=self._callback
        )
        self.stream.start()