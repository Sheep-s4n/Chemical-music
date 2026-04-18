import json
import time
import tkinter as tk
from utils.led_controller import LEDController

leds = LEDController("COM5", 300)

# -------------------------
# paramètres calibrés
# -------------------------
SEUIL_BJ_PCT = 0.14
SEUIL_JT_PCT = 0.72

COULEUR_BLEU        = (20, 60, 200)
COULEUR_JAUNE       = (240, 200, 30)
COULEUR_TRANSPARENT = (240, 240, 235)

BRIGHTNESS_MIN = 10
BRIGHTNESS_MAX = 255


def _lerp(c1, c2, t):
    return tuple(
        round(c1[i] + (c2[i] - c1[i]) * t)
        for i in range(3)
    )


def luminosite_vers_couleur(luminosite, lum_min, lum_max):
    lum = max(lum_min, min(lum_max, luminosite))
    x = (lum - lum_min) / (lum_max - lum_min)

    if x <= SEUIL_BJ_PCT:
        t = x / SEUIL_BJ_PCT
        rgb = _lerp(COULEUR_BLEU, COULEUR_JAUNE, t)

    elif x <= SEUIL_JT_PCT:
        t = (x - SEUIL_BJ_PCT) / (SEUIL_JT_PCT - SEUIL_BJ_PCT)
        rgb = _lerp(COULEUR_JAUNE, COULEUR_TRANSPARENT, t)

    else:
        rgb = COULEUR_TRANSPARENT

    brightness = round(
        BRIGHTNESS_MIN + x * (BRIGHTNESS_MAX - BRIGHTNESS_MIN)
    )

    return (*rgb, brightness)


def appliquer_brightness(r, g, b, brightness):
    facteur = brightness / 255
    return (
        int(r * facteur),
        int(g * facteur),
        int(b * facteur)
    )


# -------------------------
# fenêtre aperçu écran
# -------------------------
root = tk.Tk()
root.title("Briggs-Rauscher Preview")

canvas = tk.Canvas(root, width=300, height=300)
canvas.pack()

rect = canvas.create_rectangle(0, 0, 300, 300, fill="#000000", outline="#000000")


def update_preview(color):
    r, g, b, brightness = color
    r, g, b = appliquer_brightness(r, g, b, brightness)
    hex_color = f"#{r:02x}{g:02x}{b:02x}"
    canvas.itemconfig(rect, fill=hex_color, outline=hex_color)
    root.update_idletasks()
    root.update()


# -------------------------
# chargement données
# -------------------------
with open("./experimental_data/experiment_7.jsonl", "r", encoding="utf-8") as f:
    data = [json.loads(line) for line in f if line.strip()]

values = [p["value"] for p in data]
lum_min = min(values)
lum_max = max(values)


# -------------------------
# lecture en boucle
# -------------------------
while True:
    for i in range(len(data) - 1):
        lum = data[i]["value"]
        t1 = data[i]["time"]
        t2 = data[i + 1]["time"]
        lum

        color = luminosite_vers_couleur(lum, lum_min, lum_max)

        # LEDs
        leds.fill(color)

        # aperçu écran
        update_preview(color)

        # timing expérimental réel
        dt = max(0, t2 - t1)
        time.sleep(dt)