import os
import time
import random
import threading
import logging
from flask import Flask, jsonify, render_template_string
from geopy.distance import geodesic
from google.colab.output import eval_js


log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

GÜVENLİ_MERKEZ = (39.9250, 32.8368)
GÜVENLİ_YARIÇAP = 300

def verileri_sifirla():
    return {
        "mesafe": 0,
        "durum": "GÜVENLİ",
        "nabiz": 85,
        "lat": GÜVENLİ_MERKEZ[0],
        "lon": GÜVENLİ_MERKEZ[1]
    }

son_durum = verileri_sifirla()
simulasyon_durdur = False


html_sayfasi = """
<!DOCTYPE html>
<html>
<head>
    <title>IoT PET Takip Sistemi</title>
    <meta charset="utf-8" />
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; display: flex; height: 100vh; background: #f4f7f6; }
        #sidebar { width: 320px; padding: 25px; background: white; z-index: 1000; box-shadow: 2px 0 10px rgba(0,0,0,0.1); overflow-y: auto; }
        #map { flex-grow: 1; }
        .status-box { padding: 15px; border-radius: 10px; font-weight: bold; text-align: center; margin-bottom: 20px; border: 2px solid #ddd; }
        .status-safe { color: #1e8e3e; background: #e6f4ea; border-color: #1e8e3e; }
        .status-alarm { color: white; background: #f29900; border-color: #e67e22; animation: blinker 1s infinite; }
        .status-critical { color: white; background: #d93025; border-color: #b21f14; animation: blinker 0.4s infinite; }
        @keyframes blinker { 50% { opacity: 0.6; } }
        .data { border-bottom: 1px solid #eee; padding: 12px 0; font-size: 1.1em; }
        .pulse-val { font-size: 2em; font-weight: bold; color: #d93025; }
        .btn-audio { width: 100%; padding: 12px; background: #1a73e8; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 20px; }
        h2 { color: #1a73e8; margin-bottom: 10px; border-bottom: 2px solid #eee; padding-bottom: 5px; }
    </style>
</head>
<body>
    <div id="sidebar">
        <h2> IoT PET Takip</h2>
        <button class="btn-audio" onclick="sesiAc()">🔊 SESLERİ ETKİNLEŞTİR</button>
        <div id="box" class="status-box status-safe">Sistem Hazır</div>
        <div class="data"> <b>Anlık Nabız:</b><br><span id="nabiz" class="pulse-val">--</span> BPM</div>
        <div class="data"> <b>Uzaklık:</b><br><span id="mesafe">0.0 m</span></div>
        <div class="data"> <b>Konum:</b><br><small id="konum">-</small></div>
    </div>
    <div id="map"></div>

    <script>
        var map = L.map('map').setView([39.9250, 32.8368], 16);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
        L.circle([39.9250, 32.8368], { color: 'blue', fillOpacity: 0.1, radius: 300 }).addTo(map);
        var marker = L.marker([39.9250, 32.8368]).addTo(map);
        var rota = L.polyline([], {color: '#1a73e8', weight: 3}).addTo(map);

        var audioCtx = null;

        function sesiAc() {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            alert("Sesler aktif edildi. Lütfen izlemeye devam edin.");
        }

        function alarmCal(freq, dur, vol, type) {
            if (!audioCtx) return;
            if (audioCtx.state === 'suspended') audioCtx.resume();
            let osc = audioCtx.createOscillator();
            let gain = audioCtx.createGain();
            osc.type = type;
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            gain.gain.setValueAtTime(vol, audioCtx.currentTime);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + dur);
        }

        async function yenile() {
            try {
                const res = await fetch('/veri');
                const d = await res.json();

                document.getElementById('nabiz').innerText = d.nabiz;
                document.getElementById('mesafe').innerText = d.mesafe.toFixed(1) + " m";
                document.getElementById('konum').innerText = d.lat.toFixed(5) + ", " + d.lon.toFixed(5);

                const box = document.getElementById('box');
                if (d.nabiz < 40) {
                    box.innerText = "🚨 KRİTİK: NABIZ UYARISI!";
                    box.className = "status-box status-critical";
                    alarmCal(150, 0.8, 0.4, 'sawtooth'); // Şiddetli kalın siren
                } else if (d.durum === "ALARM") {
                    box.innerText = "⚠️ BÖLGE DIŞI!";
                    box.className = "status-box status-alarm";
                    alarmCal(880, 0.3, 0.1, 'sine'); // Normal bip
                } else {
                    box.innerText = "✅ GÜVENLİ";
                    box.className = "status-box status-safe";
                }

                var p = [d.lat, d.lon];
                marker.setLatLng(p);
                rota.addLatLng(p);
                map.panTo(p);
            } catch(e) {}
        }
        setInterval(yenile, 1500);
    </script>
</body>
</html>
"""

app = Flask(__name__)

@app.route('/')
def index():
    global son_durum
    son_durum = verileri_sifirla()
    return render_template_string(html_sayfasi)

@app.route('/veri')
def veri():
    return jsonify(son_durum)

def iot_simulasyonu():
    global son_durum, simulasyon_durdur
    while not simulasyon_durdur:

        lat_adim = random.uniform(-0.00015, 0.00025)
        lon_adim = random.uniform(-0.00015, 0.00025)

        son_durum["lat"] += lat_adim
        son_durum["lon"] += lon_adim


        if son_durum["mesafe"] > 250:
            son_durum["nabiz"] = max(30, son_durum["nabiz"] - random.randint(0, 5))
        else:
            son_durum["nabiz"] = random.randint(75, 95)


        m = geodesic(GÜVENLİ_MERKEZ, (son_durum["lat"], son_durum["lon"])).meters
        son_durum["mesafe"] = m
        son_durum["durum"] = "ALARM" if m > GÜVENLİ_YARIÇAP else "GÜVENLİ"

        time.sleep(2)


threading.Thread(target=lambda: app.run(port=5180, debug=False, use_reloader=False), daemon=True).start()
threading.Thread(target=iot_simulasyonu, daemon=True).start()

os.system('clear')
print(f" SİSTEM ÇALIŞIYOR! Link: {eval_js('google.colab.kernel.proxyPort(5180)')}")
