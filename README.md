# Overview



https://github.com/user-attachments/assets/7c9f23ff-6d8b-49c5-987c-4352c482ddcf

_The first test of Chemical Music (sound removed for copyright reasons) shows the projected diagram adapting to the reaction’s color cycles, illustrating its oscillations._


This project explores the intersection of chemistry and art through an immersive experience. The **Briggs-Rauscher reaction** was chosen for its striking color changes, which can be monitored using a photoresistor.  

The basic workflow is as follows: the microcontroller collects data from the photoresistor and sends it to the computer. This data reflects the current color of the reaction and is processed in Python to generate music while simultaneously controlling LED colors that adapt in real time to the reaction. Additionally, a chemical clock is implemented to estimate the periodic color transitions, and voice commands can be used to interact with the lighting system during the experiment.

# Hardware Setup

The project relies on external hardware to gather real-time data and control LEDs:  

- **Microcontroller:** 2 × Gelegoo Mega2560 R3 (Arduino-compatible) — one dedicated to reaction monitoring, one dedicated to LED control
- **Sensors & Components:** Photoresistor, breadboard, male-to-male jumper wires, standard electrical wires, screw terminal blocks  
- **LED Strips:** WS2811 addressable LED strip (each address controls a group of 3 LEDs)  
- **Power Supply:** 12 V 10 A switching power supply  

The two systems described below form a single pipeline: data is first acquired from the Briggs–Rauscher reaction via a photoresistor and then translated by a computer into music and by the LED system into a visual output.

## Reaction Monitoring System
The setup captures the dynamic color changes of the chemical reaction using light sensing:

  <table>
    <tr>
      <td><img width="500" height="375" src="https://github.com/user-attachments/assets/3ae6e8a6-17fa-4e8e-bff8-8710f63bf662"></td>
      <td><img width="500" height="375" src="https://github.com/user-attachments/assets/435f0629-7192-446f-a931-8ed98bbe21b3"></td>
    </tr>
  </table>


1. **Light source:** Illuminates the chemical mixture uniformly.

2. **Reaction mixture:** Color-changing reaction (e.g., Briggs–Rauscher) in a transparent container.

3. **Microcontroller:** Voltage from the photoresistor is read by the Gelegoo Mega2560 R3 (Arduino-compatible).

4. **Photoresistor:** Positioned behind the mixture; its resistance varies with transmitted light.

5. **Computer:** Receives real-time data via USB.

<img width="461" height="348" alt="photoresistor_wiring_diagram" src="https://github.com/user-attachments/assets/c4dad04c-2a9e-4077-aecb-a2140f78e7a1" />

_Photoresistor wiring diagram_


## LED Control System

  <table>
    <tr>
      <td><img width="500"  alt="AD_2_low_res" height="375" src="https://github.com/user-attachments/assets/ecf80628-9224-41da-9433-03d782b97883"></td>
      <td><img width="500" alt="PSU_wires_low_res" height="375" src="https://github.com/user-attachments/assets/57d33b4c-e179-4e0d-8304-565007264147"></td>
    </tr>
  </table>

**First image:** 

1. **PSU (Power supply unit):** Converts Alternating Current (AC) into regulated 12 V Direct Current (DC) required by the LED strips. The Arduino cannot directly power the LED system due to current limitations at 5V.

2. **LED Strip:** WS2811 addressable LED strip; each controller IC governs a segment of three LEDs. The emitted light is synchronized with the chemical reaction colors.

3. **Power Injection Cables:** additional Direct Current (DC) supply lines distributed along the strip to compensate for voltage drop over distance. See the next section for further details.

4. **LED data wire:** This green wire carries data from the microcontroller to the LED strip, controlling the color and brightness of each segment.

5. **Shared ground wire:** Provides a common electrical reference between the microcontroller and the power supply, ensuring reliable data signal interpretation.

**Second image:** 

1. **Power cord:** Supplies alternating current from the socket to the PSU.

2. **AC input wiring:** Standard three-wire configuration: live (L), neutral (N), and protective earth (PE).
   
3. **V- wires (0 V / ground return):** Return path for the 12 V DC supply distributed along the LED system.

4. **V+ wires (12 V supply rail):** DC power delivery lines supplying the LED strips.

### Power Injection Strategy

Due to resistive losses along long LED strips, voltage drop becomes significant. To maintain uniform brightness, multiple power injection points are required. These reintroduce 12 V at regular intervals along the strip. 
_Example:_

<img width="500" alt="power_injection_low_res" height="375" src="https://github.com/user-attachments/assets/61630cac-c5f4-4ba2-9eb7-e3059a54f22c">



# Notes

> Music files have been temporarily removed due to copyright restrictions. Royalty-free music will be added in the future.  

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


