## Overview



https://github.com/user-attachments/assets/7c9f23ff-6d8b-49c5-987c-4352c482ddcf

_The first test of Chemical Music (sound removed for copyright reasons) shows the projected diagram adapting to the reaction’s color cycles, illustrating its oscillations._


This project explores the intersection of chemistry and art through an immersive experience. The **Briggs-Rauscher reaction** was chosen for its striking color changes, which can be monitored using a photoresistor.  

The basic workflow is as follows: the microcontroller collects data from the photoresistor and sends it to the computer. This data reflects the current color of the reaction and is processed in Python to generate **music**. Additionally, a **chemical clock** is implemented, as the color changes occur periodically.  


## Hardware Setup

The project relies on external hardware to gather real-time data:  

- **Microcontroller:** Gelegoo Mega2560 R3 (Arduino-compatible)  
- **Sensors & Components:** Photoresistor, breadboard, male-to-male jumper wires  
- **LED Strips:** WS2812B addressable LEDs (currently under development)  


The setup captures the dynamic color changes of the chemical reaction using light sensing:

<img width="417" height="313" alt="assembly_diagram_low_quality" src="https://github.com/user-attachments/assets/3ae6e8a6-17fa-4e8e-bff8-8710f63bf662" />
<img width="417" height="313" alt="assembly_diagram_low_quality" src="https://github.com/user-attachments/assets/435f0629-7192-446f-a931-8ed98bbe21b3" />



1. **Light source:** Illuminates the chemical mixture uniformly.

2. **Reaction mixture:** Color-changing reaction (e.g., Briggs–Rauscher) in a transparent container.

3. **Microcontroller:** Voltage from the photoresistor is read by the Gelegoo Mega2560 R3 (Arduino-compatible).

4. **Photoresistor:** Positioned behind the mixture; its resistance varies with transmitted light.

<img width="461" height="348" alt="photoresistor_wiring_diagram" src="https://github.com/user-attachments/assets/c4dad04c-2a9e-4077-aecb-a2140f78e7a1" />

_Photoresistor wiring diagram_

5. **Computer:** Receives real-time data via USB.


## Work in Progress

- Responsive LED strip control synchronized with chemical music  

> **Note:** Music files have been temporarily removed due to copyright restrictions. Royalty-free music will be added in the future.  

> **Voice Recognition & Voice-Control Model**
>
> The AI model required for voice recognition and voice-based LED control is **not included by default** in this project.
>
> It must be downloaded manually from the official Vosk model repository:
>
> https://alphacephei.com/vosk/models
>
> Model used in this project:
> - `vosk-model-small-fr-0.22` (French)
>
> After downloading, place the model in the appropriate project directory and configure the path in your application before running voice recognition features.


