import serial
import serial.tools.list_ports
import threading
import time
from collections import deque
from statistics import mean


class OscillationTracker:
    def __init__(
        self,
        port="COM4",
        baudrate=9600,
        threshold=400,
        count_required=5,
        smooth_size=30,
        buffer_size=2000,
        period_avg_count=2
    ):
        # -------------------------
        # Serial
        # -------------------------
        self.port = port
        self.baudrate = baudrate
        self.ser = serial.Serial(self.port, self.baudrate, timeout=1)

        # -------------------------
        # Detection settings
        # -------------------------
        self.threshold = threshold
        self.count_required = count_required
        self.period_avg_count = period_avg_count

        # -------------------------
        # Shared values
        # -------------------------
        self.raw_value = 0
        self.smoothed_value = 0

        self.just_went_up = False
        self.just_went_down = False

        self.state = None
        self.above_count = 0
        self.below_count = 0

        # cycle = UP -> DOWN -> next UP
        self.cycle_count = 0
        self.waiting_for_next_up = False

        # -------------------------
        # Clock data
        # -------------------------
        self.up_transition_times = []
        self.periods = []

        self.clock_initialized = False
        self.chemical_clock_period = None
        self.chemical_clock_time = 0
        self.phase_error = 0

        # -------------------------
        # Buffers
        # -------------------------
        self.data_buffer = deque(maxlen=buffer_size)
        self.smooth_buffer = deque(maxlen=smooth_size)

        # -------------------------
        # Thread control
        # -------------------------
        self.running = False
        self.thread = None

    # -------------------------
    # Utility
    # -------------------------
    def _smooth(self, value):
        self.smooth_buffer.append(value)
        self.smoothed_value = sum(self.smooth_buffer) / len(self.smooth_buffer)
        return self.smoothed_value

    # -------------------------
    # Transition logic
    # -------------------------
    def _process_value(self, value):
        #self.just_went_up = False // audio_engine will turn it false when it has processed the transition
        self.just_went_down = False

        if value > self.threshold:
            self.above_count += 1
            self.below_count = 0

        elif value < self.threshold:
            self.below_count += 1
            self.above_count = 0

        else:
            self.above_count = 0
            self.below_count = 0

        # -------------------------
        # UP transition
        # -------------------------
        if self.above_count >= self.count_required and self.state != "high":
            self.state = "high"
            self.above_count = 0
            self.just_went_up = True

            now = time.time()
            self.up_transition_times.append(now)
            print(f"Transition UP detected at value {value} (cycle {self.cycle_count + 1})")

            # cycle restart
            if self.waiting_for_next_up:
                self.cycle_count += 1
                self.waiting_for_next_up = False

            # clock period calculation
            if len(self.up_transition_times) >= 2:
                new_period = self.up_transition_times[-1] - self.up_transition_times[-2]

                if not self.clock_initialized:
                    self.periods.append(new_period)

                    if len(self.periods) >= self.period_avg_count:
                        self.chemical_clock_period = mean(self.periods)
                        self.chemical_clock_time = now
                        self.clock_initialized = True

                else:
                    self.chemical_clock_time += self.chemical_clock_period
                    self.phase_error = now - self.chemical_clock_time

        # -------------------------
        # DOWN transition
        # -------------------------
        if self.below_count >= self.count_required and self.state != "low":
            self.state = "low"
            self.below_count = 0
            self.just_went_down = True

            # half cycle completed
            self.waiting_for_next_up = True

    # -------------------------
    # Main loop
    # -------------------------
    def _loop(self):
        while self.running:
            try:
                line = self.ser.readline().decode("utf-8").strip()

                if not line:
                    continue

                value = int(line)

                self.raw_value = value
                smoothed = self._smooth(value)

                self.data_buffer.append(smoothed)

                self._process_value(value)

            except ValueError:
                continue


    # -------------------------
    # Public API
    # -------------------------
    def start(self):
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

        if self.thread:
            self.thread.join(timeout=1)

        if self.ser:
            self.ser.close()

    # -------------------------
    # Convenience getters
    # -------------------------
    def get_brightness_input(self):
        return self.smoothed_value

    def get_plot_data(self):
        return list(self.data_buffer)