from visuals.clock_ui import ChemicalClockUI


class ClockDisplay:
    def __init__(self, tracker, x_min=0, x_max=700):
        self.tracker = tracker
        self.ui = ChemicalClockUI()
        self.x_min = x_min
        self.x_max = x_max

    def update(self):
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
                self.tracker.period_avg_count
            )
        else:
            self.ui.draw_active(
                self.tracker.chemical_clock_time,
                self.tracker.chemical_clock_period,
                self.tracker.phase_error
            )

        self.ui.update()