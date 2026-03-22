## Overview

This project explores the intersection of chemistry and art through an immersive experience. The **Briggs-Rauscher reaction** was chosen for its striking color changes, which can be monitored using a photoresistor.  

The basic workflow is as follows: the microcontroller collects data from the photoresistor and sends it to the computer. This data reflects the current color of the reaction and is processed in Python to generate **music**. Additionally, a **chemical clock** is implemented, as the color changes occur periodically.  

Example of the Briggs-Rauscher reaction:  

https://github.com/user-attachments/assets/d78ce497-1482-41fd-b8a9-8b21e28738da


<video  width="640"  height="360"  controls>  
<source  src="https://USERNAME.github.io/REPO/assets/video/reaction_demo.mp4"  type="video/mp4">  
Your browser does not support the video tag.  
</video>

## Hardware Setup

The project relies on external hardware to gather real-time data:  

- **Microcontroller:** Gelegoo Mega2560 R3 (Arduino-compatible)  
- **Sensors & Components:** Photoresistor, breadboard, male-to-male jumper wires  
- **LED Strips:** WS2812B addressable LEDs (currently under development)  

## Work in Progress

- Responsive LED strip control synchronized with chemical music  
- JSON-based file structure for music implementation, enabling easier mapping of musical events to reaction color changes  

> **Note:** Music files have been temporarily removed due to copyright restrictions. Royalty-free music will be added in the future.  



