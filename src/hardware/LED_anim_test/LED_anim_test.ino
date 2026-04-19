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

    bool wasBlue = (prevP >= THRESHOLD);
    bool isBlue  = (p >= THRESHOLD);

    uint8_t oldSat = (uint8_t)(prevP * (255.0 / THRESHOLD));
    uint8_t newSat = (uint8_t)(p     * (255.0 / THRESHOLD));

    // ------------------------------------
    // yellow family animation
    // ------------------------------------
    if (!wasBlue && !isBlue) {


        int step = (newSat > oldSat) ? 1 : -1;

        for (int i = oldSat; i != newSat; i += step) {
            fill_solid(leds, NUM_LEDS, CHSV(56, i, 175));
            FastLED.show();
            delay(20);
        }

        fill_solid(leds, NUM_LEDS, CHSV(56, newSat, 175));
        FastLED.show();
    }

    // ------------------------------------
    // yellow -> blue transition
    // ------------------------------------
    else if (!wasBlue && isBlue) {

        for (int i = 175; i >= 0; i-= 10) {
            fill_solid(leds, NUM_LEDS, CHSV(56, oldSat, i));
            FastLED.show();
        }
        for (int i = 0; i <= 175; i+= 10) {
            fill_solid(leds, NUM_LEDS, CHSV(165, 255, i));
            FastLED.show();
        }
        // transition animation

    }

    // ------------------------------------
    // stable blue
    // ------------------------------------
    else if (wasBlue && isBlue) {

        // solid blue : 今分かりません、まだ考えています。 :D

    }

    // ------------------------------------
    // blue -> yellow transition
    // ------------------------------------
    else if (wasBlue && !isBlue) {

        // transition animation
        for (int i = 255; i >= 0; i-= 5) {
            fill_solid(leds, NUM_LEDS, CHSV(165, i , 175));
            FastLED.show();
        }
    }

    prevP = p;
}

void loop() {

    // simple smooth oscillation for testing
    globalP += 0.2;
    if (globalP > 1) globalP = 0;

    briggsRauscher(globalP);

    FastLED.show();
    delay(250);
}