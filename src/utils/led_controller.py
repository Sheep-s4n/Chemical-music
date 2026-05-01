import serial


START_MARKER = 0xFF

TYPE_LIGHT_UP = 0
TYPE_BRIGGS_RAUSCHER = 1
TYPE_FLASH_LEDS = 2
TYPE_FADE_OUT = 3
TYPE_BREATHING = 4
TYPE_LED_SECTION = 5
MAX_SEGMENTS = 10 # avoiding buffer overflow (41 bytes max in 64 byte buffer)

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

    def flash_leds(self):
        self._send_packet(TYPE_FLASH_LEDS)
    
    def briggs_rauscher(self, p):
        """
        p : float from 0.0 to 1.0
        converted into one byte (0-255)
        """
        p_byte = max(0, min(255, int(p * 255)))
        self._send_packet(TYPE_BRIGGS_RAUSCHER, [p_byte])
    
    
    def fade_out(self):
        self._send_packet(TYPE_FADE_OUT)
        
    def breathing(self, duration_ms):
        # manually pack/unpack the 3-byte duration (max ~16.7 million ms = ~4.6 hours)
        self._send_packet(TYPE_BREATHING, [
            (duration_ms >> 16) & 0xFF, # extract the highest byte
            (duration_ms >> 8) & 0xFF,
            duration_ms & 0xFF
        ])
        
    def led_sections(self, segments):
        """
        segments: list of (start, end)
        Example: [(0, 10), (45, 70), (120, 150)]
        """

        if len(segments) == 0:
            raise ValueError("At least one segment is required")

        if len(segments) > MAX_SEGMENTS:
            raise ValueError(f"Too many segments (max {MAX_SEGMENTS} with 64-byte payload)")

        payload = [len(segments)] # first byte is the number of segments

        for start, end in segments:
            if not (0 <= start < 300 and 0 <= end < 300):
                raise ValueError("LED indices must be between 0 and 299")

            if start > end:
                raise ValueError("start must be <= end")

            payload.extend([
                (start >> 8) & 0xFF,
                start & 0xFF,
                (end >> 8) & 0xFF,
                end & 0xFF
            ])

        self._send_packet(TYPE_LED_SECTION, payload)

    def close(self):
        self.serial.close()