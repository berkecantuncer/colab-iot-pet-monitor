# IoT Pet Tracking Simulation 🐾

This project is a real-time IoT simulation designed to track a pet's location and monitor its vital signs (heart rate). It is built using Python and Flask for the backend, and Leaflet.js for the frontend map rendering.

## Features
* **Real-Time GPS Tracking:** Simulates pet movement on a live map using Geopy and Leaflet.
* **Geofencing Alarm:** Triggers a visual and audio warning if the pet moves beyond the 300-meter safe zone radius.
* **Health Monitoring:** Simulates heart rate (BPM). Triggers a critical siren alarm if the heart rate drops below a dangerous threshold.
* **Google Colab Ready:** Specifically structured to run seamlessly on Google Colab using `google.colab.output.eval_js` for port proxying.

## Tech Stack
* **Backend:** Python, Flask, Geopy
* **Frontend:** HTML/CSS, JavaScript, Leaflet.js
* **Environment:** Google Colab

## How to Run
1. Open Google Colab.
2. Paste the script into a new notebook cell.
3. Run the cell.
4. Click the link generated in the terminal output to open the live tracking dashboard.
