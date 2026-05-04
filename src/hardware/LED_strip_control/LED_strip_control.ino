#include <FastLED.h>

#define LED_PIN 6
#define NUM_LEDS 300
#define START_MARKER 0xFF  // header byte
CRGB leds[NUM_LEDS];


uint8_t type;
uint8_t len;
uint8_t idx; // This is a counter used while reading payload bytes.
uint8_t payload[64]; 

int state = 0; // It defines which part of the message we are currently reading.


void flashLEDs() {
    uint8_t originalBrightness = FastLED.getBrightness();

    FastLED.setBrightness(255);
    FastLED.show();
    delay(100);

    FastLED.setBrightness(originalBrightness);
    FastLED.show();
}

void briggsRauscher(float p) {

    const float THRESHOLD = 0.5;

    //static bool wasBlue = false;
    //static float prevP = 0;

    //bool isBlue  = (p > THRESHOLD);

    //float prevT       = prevP / THRESHOLD;
    //uint8_t oldSat    = (uint8_t)(255 * pow(prevT, 0.6));  // what's actually on the LEDs

    // ------------------------------------
    // fixing brightness at 175
    // ------------------------------------
    FastLED.setBrightness(175);


    // ------------------------------------
    // white-yellow blend
    // ------------------------------------
    if (p <= THRESHOLD) {
        float t = p / THRESHOLD;             // 0.0 = white, 1.0 = yellow
        float t_biased = pow(t, 0.6);        // at midpoint: 0.5^0.6 ≈ 0.66 → ~65% toward yellow

        uint8_t sat = (uint8_t)(255 * t_biased);           // 0 at white, 255 at yellow

        fill_solid(leds, NUM_LEDS, CHSV(56, sat, 175));
        FastLED.show();
    }
    // ------------------------------------
    // stable blue
    // ------------------------------------
    else { // 0.75 for blue
        fill_solid(leds, NUM_LEDS, CHSV(165, 255, 175));
        FastLED.show();
    }

    /*
    // ------------------------------------
    // yellow -> blue transition
    // ------------------------------------
    else if (!wasBlue && isBlue) {

        // fade out yellow from current brightness
        for (int i = 175; i >= 0; i -= 18) {
            fill_solid(leds, NUM_LEDS, CHSV(56, oldSat, i));
            FastLED.show();
        }
        fill_solid(leds, NUM_LEDS, CHSV(56, oldSat, 0));
        FastLED.show();
        // fade in blue
        for (int i = 0; i <= 175; i += 18) {
            fill_solid(leds, NUM_LEDS, CHSV(165, 255, i));
            FastLED.show();
        }
        fill_solid(leds, NUM_LEDS, CHSV(165, 255, 175));
        FastLED.show();

    }
    */



    // ------------------------------------
    // blue -> yellow transition
    // ------------------------------------
    /*else if (wasBlue && !isBlue) {

        // transition animation
        for (int i = 255; i >= 0; i -= 26) {
            fill_solid(leds, NUM_LEDS, CHSV(165, i, 175));
            FastLED.show();
        }
        fill_solid(leds, NUM_LEDS, CHSV(165, 0, 175));
        FastLED.show();
    }

    prevP = p;
    wasBlue = isBlue;*/

}


void waveFromPoint(int origin) {

  float radius = 0;

  while (radius < NUM_LEDS) {

    for (int i = 0; i < NUM_LEDS; i++) {

      float dist = abs(i - origin);
      float intensity = 1.0 - (dist / radius);

      if (intensity < 0) intensity = 0;

      uint8_t brightness = intensity * 255;

      leds[i] = CHSV(0, 0, brightness);    
    }

    FastLED.show();

    radius += 5;     // speed of propagation
    delay(20);       // frame rate (20ms = ~50 FPS)
  }
}

void fadeOutFromCurrent(int frameDelay = 10) {

  // 1. snapshot original brightness
  uint8_t original[NUM_LEDS];

  for (int i = 0; i < NUM_LEDS; i++) {
    original[i] = leds[i].getAverageLight();
  }

  float factor = 1.0;

  // 2. exponential decay over time
  while (factor > 0.01) {

    for (int i = 0; i < NUM_LEDS; i++) {

      uint8_t v = original[i] * factor;
      leds[i] = CHSV(0, 0, v);
    }

    FastLED.show();

    factor -= 0.07;   // linear decay curve
    delay(frameDelay);
  }

  fill_solid(leds, NUM_LEDS, CRGB::Black);
  FastLED.show();
}

void ledSection(uint8_t* data, uint8_t len) {
    uint8_t numSegments = data[0];

    FastLED.setBrightness(255);
    fill_solid(leds, NUM_LEDS, CRGB::Black);

    for (uint8_t s = 0; s < numSegments; s++) {
        uint8_t base = 1 + s * 4;

        uint16_t start = ((uint16_t)data[base]     << 8) | data[base + 1];
        uint16_t end   = ((uint16_t)data[base + 2] << 8) | data[base + 3];

        start = min(start, (uint16_t)(NUM_LEDS - 1));
        end   = min(end,   (uint16_t)(NUM_LEDS - 1));

        if (start <= end) {
            fill_solid(leds + start, end - start + 1, CRGB::White);
        }
    }

    FastLED.show();
}


void breathingAnimation(uint32_t durationMs) {

  uint32_t startTime = millis();

  // -------------------------
  // snapshot current LED state
  // -------------------------
  CRGB original[NUM_LEDS];

  for (int i = 0; i < NUM_LEDS; i++) {
    original[i] = leds[i];
  }

  uint8_t startBrightness = FastLED.getBrightness();

  // -------------------------
  // BREATHING PHASE
  // -------------------------
  while (millis() - startTime < durationMs) {

    uint8_t b = beatsin8(20, 100, 255);

    FastLED.setBrightness(b);
    FastLED.show();

    delay(10);
  }

  // -------------------------
  // SMOOTH RESTORE PHASE
  // -------------------------

  uint8_t current = FastLED.getBrightness();

  while (current != startBrightness) {

    if (current > startBrightness) current--;
    else current++;

    FastLED.setBrightness(current);

    // restore original LED colors
    for (int i = 0; i < NUM_LEDS; i++) {
      leds[i] = original[i];
    }

    FastLED.show();
    delay(10);
  }

  FastLED.setBrightness(startBrightness);
}

void execute(uint8_t type, uint8_t* data, uint8_t len) {

    if (type == 0) {
        waveFromPoint(150);
    }

    else if (type == 1) {
        float p = data[0] / 255.0f;
        briggsRauscher(p);
    }

    else if (type == 2) {
        flashLEDs();
    }

    else if (type == 3) {
        fadeOutFromCurrent();
    }

    else if (type == 4) {
        uint32_t durationMs =
            ((uint32_t)data[0] << 16) |
            ((uint32_t)data[1] << 8) |
            (uint32_t)data[2];

        breathingAnimation(durationMs);
    }

    else if (type == 5) {
      ledSection(data, len);
    }
    // switch statment broke the code for whatever reason ... 
}

void setup() {
  Serial.begin(115200);
  FastLED.addLeds<WS2811, LED_PIN, BRG>(leds, NUM_LEDS);
  FastLED.clear();  // to ensure all leds aren't lit before letting the python code handle the leds
  FastLED.show();
}


void loop() {
    while (Serial.available()) {
        uint8_t b = Serial.read(); // reads one byte the next one will be read in the next loop iteration, this way we can process the message byte by byte without blocking until the whole message is received
        switch (state) {

        case 0: // waiting for start
            if (b == START_MARKER) state = 1;
            break;

        case 1: // type
            type = b;
            state = 2;
            break;

        case 2: // length
            len = b;
            idx = 0;
            if (len > 0) {
                state = 3;
            } else {
                execute(type, payload, len); // we have all the data (no payload) so we can execute the command immediately
                state = 0;
            }
            break;

        case 3: // payload
            payload[idx++] = b;
            if (idx >= len) {
                execute(type, payload, len); // we have all the data so we can execute the command
                state = 0;
            }
            break;
        }
    }
}