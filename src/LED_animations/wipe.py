
def white_wipe(num_leds):
    """
    Generator that yields frames for a 'progressive white fill' animation.
    Each LED turns white one after another.
    """
    # Start fully black
    frame = [(0, 0, 0, 0) for _ in range(num_leds)]
    yield frame.copy() # the first iteration explicitly initializes the strip to black

    for i in range(0, num_leds, 4):  # step of 4
        for j in range(4):          # fill a block of 4 LEDs
            if i + j < num_leds:
                frame[i + j] = (255, 255, 255, 100)

        yield frame.copy()
        
def black_wipe(num_leds):
    """
    Generator that yields frames for a 'progressive blackout' animation.
    Each LED turns off (black) in blocks of 4.
    """
    # Start fully white
    frame = [(255, 255, 255, 100) for _ in range(num_leds)]
    yield frame.copy()

    for i in range(0, num_leds, 4):
        for j in range(4):
            if i + j < num_leds:
                frame[i + j] = (0, 0, 0, 0)

        yield frame.copy()
        
def black_wipe_reverse(num_leds):
    """
    Progressive blackout starting from the end of the strip.
    """
    # Start fully white
    frame = [(255, 255, 255, 100) for _ in range(num_leds)]
    yield frame.copy()

    for i in range(num_leds - 1, -1, -4):  # start from end
        for j in range(4):
            idx = i - j
            if idx >= 0:
                frame[idx] = (0, 0, 0, 0)

        yield frame.copy()