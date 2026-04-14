def fade_out(num_leds, steps=20):
    """
    Fade out by reducing only the brightness channel.
    Keeps RGB constant at white.
    """
    frame = [(255, 255, 255, 100) for _ in range(num_leds)]

    for s in range(steps + 1):
        factor = 1 - (s / steps)
        brightness = int(100 * factor)

        frame = [(255, 255, 255, brightness) for _ in range(num_leds)]

        yield frame