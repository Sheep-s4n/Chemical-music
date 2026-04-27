from visuals.clock_ui import ChemicalClockUI
DEFAULT_ASSUMED_MIN = 0
DEFAULT_ASSUMED_MAX = 700

class ClockDisplay:
    def __init__(self, tracker, x_min=DEFAULT_ASSUMED_MIN, x_max=DEFAULT_ASSUMED_MAX):
        self.tracker = tracker
        self.ui = None
        self.x_min = x_min
        self.x_max = x_max
        
    def update(self):
    
        if self.ui is None : 
            self.ui = ChemicalClockUI()

        if self.x_min == DEFAULT_ASSUMED_MIN and self.x_max == DEFAULT_ASSUMED_MAX: # only assigns once the new max and new min
            if (
                self.tracker.min_value != float("inf")
                and self.tracker.max_value != float("-inf")
            ):
                self.x_min = self.tracker.min_value
                self.x_max = self.tracker.max_value

        
        self.ui.handle_events()

        self.ui.update_background(
            self.tracker.smoothed_value,
            self.x_min,
            self.x_max
        )

        if not self.tracker.clock_initialized:
            self.ui.draw_init(
                self.tracker.periods,
                self.tracker.chemical_clock_period,
                self.tracker.period_target
            )
        else:
            self.ui.draw_active(
                self.tracker.chemical_clock_time,
                self.tracker.chemical_clock_period,
                self.tracker.phase_error
            )

        self.ui.update()