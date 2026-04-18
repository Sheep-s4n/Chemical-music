import serial


START_MARKER = 0xFF

TYPE_LIGHT_UP = 0
TYPE_COLOR_TRANSITION = 1
TYPE_BRIGHTNESS_SPIKE = 2
TYPE_FADE_OUT = 3
TYPE_BREATHING = 4

class LEDController:
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)

    def _send_packet(self, packet_type, payload=None):
        if payload is None: payload = []

        length = len(payload)

        packet = bytes([
            START_MARKER,
            packet_type,
            length,
            *payload #  * --> unpack a list/tuple into separate arguments
        ])
        print(packet)

        self.serial.write(packet)

    def light_up(self):
        self._send_packet(TYPE_LIGHT_UP)

    def transition_to(self, r, g, b):
        self._send_packet(TYPE_COLOR_TRANSITION, [r, g, b])

    def brightness_spike(self):
        self._send_packet(TYPE_BRIGHTNESS_SPIKE)
    
    def fade_out(self):
        self._send_packet(TYPE_FADE_OUT)
        
    def breathing(self, duration_ms):
        # manually pack/unpack the 3-byte duration (max ~16.7 million ms = ~4.6 hours)
        self._send_packet(TYPE_BREATHING, [
            (duration_ms >> 16) & 0xFF, # extract the highest byte
            (duration_ms >> 8) & 0xFF,
            duration_ms & 0xFF
        ])

    def close(self):
        self.serial.close()