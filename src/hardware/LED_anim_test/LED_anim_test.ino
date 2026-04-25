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
    for (int i = 0; i < NUM_LEDS; i++) {
        leds[i] = CRGB::Blue;
    }
    FastLED.setBrightness(175);
    FastLED.show();
}


void flashLEDs() {
    uint8_t originalBrightness = FastLED.getBrightness();

    FastLED.setBrightness(255);
    FastLED.show();
    delay(100);

    FastLED.setBrightness(originalBrightness);
    FastLED.show();
}

void loop() {
    delay(3000);
    flashLEDs();
}