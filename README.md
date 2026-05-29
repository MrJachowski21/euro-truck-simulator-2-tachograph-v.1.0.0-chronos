# Chronos TachoSystem v1.0.0 (Retro Edition)

Chronos TachoSystem is a real-time digital tachograph styled after classic VDO Siemens devices, designed for drivers of virtual transport companies and fans of the Euro Truck Simulator 2 (ETS2) game.

The application works directly with the telemetry server, automatically distinguishing and recording driver activity states (Driving, Working, Resting) based on game time and vehicle behavior. This is the first official system version (v1.0.0).

--

## 🚀 New in version 1.0.0

* **Digital Tacho Printer (24-Hour Print):** Added functionality for generating full daily reports, broken down by driver, continuous driving time, daily driving time, and resting time. Data is printed in the console and saved to the text file `wydruk_tacho.txt`. * **Multi-Driver System:** Full support for two driver slots (Slot 1: [DRIVER 1], Slot 2: [DRIVER 2] with independent resetting of drive cycle counters after card change.
* **New Pixel Interface (VDO Style):** The LCD display layout (Tkinter Canvas) has been redesigned. Text has improved margins (X=15) and the `Consolas` font, which prevents text edges from being cut off and perfectly reflects the actual device.
* **Official Telemetry Support v3.2.5:** Full integration with the latest, stable version of the Funbit telemetry server.

---

## 📦 System Requirements and Modules

The project was written in Python and relies solely on the **standard library**, meaning you don't need to install any additional packages via `pip`!**

* `tkinter` (Built-in GUI library)
* `json` & `urllib` (Built-in HTTP query support and API framework)
* `threading` & `time` (Support for multithreaded data downloads)

---

## 📄 User Manual and Installation Guide

Full, detailed instructions for installing the environment, configuring the telemetry server, and properly launching the tachograph are included in the **PDF** file attached to the project.

Before launching the application for the first time, please read the PDF document to ensure the plugin (`.dll` plugin) is correctly installed in the Euro Truck Simulator 2 directory.

---

## 🖥️ LCD Screen Navigation (5 Views)

Use the navigation buttons (▲ / ▼) on the tachograph casing to switch between five dedicated screens:
1. **Main Screen:** Current in-game time, activity status (▶, ⚒, h), and cycle time and daily total.
2. **Work Details:** Accurate counter for other work and the current uninterrupted daily rest.
3. **Digital Speedometer:** Current vehicle speed (V = km/h) retrieved directly from the game bus.
4. **Status Screen:** Graphical and clear representation of the current work mode using system icons. 5. **Bus Status:** Displays the IP address, port (`25555`), and version of the connected telemetry.

--

## 📝 License and Acknowledgements
Developed using open-source software:
* Telemetry Server: [Funbit ETS2 Telemetry Server](https://github.com/Funbit/ets2-telemetry-server)
* Appearance and runtime logistics: Inspired by VDO Siemens digital tachograph systems.

*Release v1.0.0 - Initial, Stable Version.*
