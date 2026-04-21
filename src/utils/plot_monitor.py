import matplotlib.pyplot as plt
import threading
import time


class PlotMonitor:
    def __init__(self, tracker):
        self.tracker = tracker
        self.running = False

    def _loop(self):
        plt.ion()
        fig, ax = plt.subplots()
        line, = ax.plot([], [], lw=2)

        while self.running:
            data = self.tracker.get_plot_data()

            if len(data) > 1:
                line.set_data(range(len(data)), data)
                ax.set_xlim(0, len(data))
                ax.set_ylim(min(data) - 50, max(data) + 50)

                fig.canvas.draw()
                fig.canvas.flush_events()

            time.sleep(0.02)

    def start(self):
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False