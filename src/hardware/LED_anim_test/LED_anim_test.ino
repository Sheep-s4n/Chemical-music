#include <FastLED.h>

#define LED_PIN 6
#define NUM_LEDS 300

CRGB leds[NUM_LEDS];

const float THRESHOLD = 0.6;

float globalP = 0;
bool wasBlue = false;

void setup() {
    Serial.begin(115200);

    FastLED.addLeds<WS2811, LED_PIN, BRG>(leds, NUM_LEDS);

    FastLED.clear();
    FastLED.show();
}

void briggsRauscher(float p) {

    static float prevP = 0;
    static uint8_t fadeT = 0;
    static bool fading = false;

    // ---------- YELLOW PHASE ----------
    if (p < THRESHOLD) {

        wasBlue = false;

        uint8_t sat = (uint8_t)(p * (255.0 / THRESHOLD));
        uint8_t hue = 56;

        for (int i = 0; i < NUM_LEDS; i++) {
            leds[i] = CHSV(hue, sat, 175);
        }

        fading = false;
    }

    // ---------- BLUE PHASE ----------
    else {

        uint8_t blueHue = 160;

        // first entry into blue → start fade
        if (!wasBlue && prevP < THRESHOLD) {
            fading = true;
            fadeT = 0;
            wasBlue = true;
        }

        if (fading) {

            CRGB startColor = CHSV(56, 255, 175);
            CRGB endColor   = CHSV(blueHue, 255, 175);

            for (int i = 0; i < NUM_LEDS; i++) {
                leds[i] = blend(startColor, endColor, fadeT);
            }

            fadeT += 5;

            if (fadeT >= 255) {
                fading = false;
            }
        }
        else {
            for (int i = 0; i < NUM_LEDS; i++) {
                leds[i] = CHSV(blueHue, 255, 175);
            }
        }
    }

    prevP = p;
}

void loop() {

    // simple smooth oscillation for testing
    globalP += 0.05;
    if (globalP > 1) globalP = 0;

    briggsRauscher(globalP);

    FastLED.show();
    delay(500);
}