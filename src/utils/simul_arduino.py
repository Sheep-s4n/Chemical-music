
import time
import json

class PhotoresistorSimulator:
    def __init__(self, period):
        """
        period : total duration of one full cycle (seconds)
        """
        if period <= 1:
            raise ValueError("Period must be > 1 second (plateau alone lasts 1s).")

        self.period = period
        self.start_time = time.monotonic()

        # Phase durations (fractions of remaining time)
        remaining = period - 1.0  # reserve 1s for plateau
        self.t1 = 0.40 * remaining  # slow rise
        self.t2 = 0.20 * remaining  # fast rise
        self.t4 = 0.40 * remaining  # decay

    def read(self):
        """
        Returns a simulated analog value in [30, 700].
        """
        t = (time.monotonic() - self.start_time) % self.period

        # Phase 1: slow rise (30 → 200)
        if t < self.t1:
            x = t / self.t1
            return int(30 + (200 - 30) * x**1.5)

        t -= self.t1

        # Phase 2: fast rise (200 → 700)
        if t < self.t2:
            x = t / self.t2
            return int(200 + (700 - 200) * x**4)

        t -= self.t2

        # Phase 3: plateau (700 for 1s)
        if t < 1.0:
            return 700

        t -= 1.0

        # Phase 4: decay (700 → 30)
        x = t / self.t4
        return int(700 - (700 - 30) * x**2)


class RealDataSimulator:
    def __init__(self, filename, sample_interval=0.015, loop=True):
        """
        filename : path to valeurs_exp.json
        sample_interval : seconds between samples (controls playback speed)
        loop : restart when reaching end
        """
        with open(filename, "r") as f:
            self.data = json.load(f)

        self.sample_interval = sample_interval
        self.loop = loop

        self.index = 0
        self.last_time = time.monotonic()

    def read(self):
        now = time.monotonic()

        elapsed = now - self.last_time
        steps = int(elapsed / self.sample_interval)

        if steps > 0:
            self.last_time += steps * self.sample_interval
            self.index += steps

            if self.loop:
                self.index %= len(self.data)
            else:
                self.index = min(self.index, len(self.data) - 1)

        time.sleep(self.sample_interval)
        return self.data[self.index]
