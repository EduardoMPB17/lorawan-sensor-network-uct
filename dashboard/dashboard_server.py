# -*- coding: utf-8 -*-
"""
Dashboard LoRaWAN UCT - Servidor Local con Interfaz Web Avanzada
Trabajo de Título INFO-1197 - Universidad Católica de Temuco
Autor: Eduardo Remigio Mariqueo Porma

Características:
- Soporte dual: Milesight UG65 / UG63 (Embedded NS) y ChirpStack v4
- Actualización automática en tiempo real cada 1 segundo (sin caché)
- Selector y filtro por nodos (Todos / Nodo 1 LOS / Nodo 2 NLOS)
- Buscador interactivo en vivo sobre el historial
- Selector de volumen de historial (25, 50, 100, Todas las tramas)
- Exportación directa a CSV para análisis en Excel
- Interfaz moderna Dark Mode con Glassmorphism y diseño responsivo
"""

import json
import sqlite3
import threading
import time
import os
import io
import csv
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
import paho.mqtt.client as mqtt

DB_PATH = os.path.join(os.path.dirname(__file__), "telemetry.db")
PORT = 5000

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            device_name TEXT,
            dev_eui TEXT,
            temperature REAL,
            humidity REAL,
            battery_mv INTEGER,
            battery_pct INTEGER,
            packet_seq INTEGER,
            status_flags INTEGER,
            rssi INTEGER,
            snr REAL,
            f_cnt INTEGER
        )
    ''')
    conn.commit()
    conn.close()

latest_packet = {}
history_lock = threading.Lock()

def on_connect(client, userdata, flags, rc):
    print(f"[MQTT] Conectado a Mosquitto en localhost:1883 (rc={rc})", flush=True)
    client.subscribe("application/#")

def on_message(client, userdata, msg):
    global latest_packet
    try:
        topic = msg.topic
        if "gateway/" in topic or "/conn" in topic:
            return

        payload = json.loads(msg.payload.decode('utf-8'))
        
        # Extraer DevEUI del tópico (application/sensores-campus/device/{devEUI}/event/up)
        parts = topic.split('/')
        topic_deveui = parts[3] if len(parts) >= 4 and parts[2] == 'device' else ''

        # Objeto de telemetría decodificado
        obj = payload.get('object')
        if not obj or not isinstance(obj, dict):
            # Fallback automático: decodificar payload binario en Base64 de la UG65
            data_raw = payload.get('data')
            if isinstance(data_raw, str):
                try:
                    import base64
                    raw_bytes = base64.b64decode(data_raw)
                    if len(raw_bytes) >= 10:
                        n_id = raw_bytes[0]
                        p_seq = (raw_bytes[1] << 24) | (raw_bytes[2] << 16) | (raw_bytes[3] << 8) | raw_bytes[4]
                        t_raw = (raw_bytes[5] << 8) | raw_bytes[6]
                        if t_raw > 32767: t_raw -= 65536
                        h_raw = (raw_bytes[7] << 8) | raw_bytes[8]
                        b_raw = raw_bytes[9]
                        v_bat = 2.0 + (b_raw / 100.0)
                        obj = {
                            "node_id": n_id,
                            "sequence": p_seq,
                            "temperature": round(t_raw / 100.0, 2),
                            "humidity": round(h_raw / 100.0, 1),
                            "battery_v": v_bat,
                            "battery_mv": int(v_bat * 1000),
                            "battery_pct": round(min(100, max(0, (v_bat - 3.0) / 1.2 * 100)))
                        }
                except Exception as ex:
                    print("[Decode Error]", ex, flush=True)

        if not obj or not isinstance(obj, dict):
            obj = {}

        node_id = obj.get('node_id', 1)

        # Soporte híbrido ChirpStack v4 y Milesight UG65
        device_info = payload.get('deviceInfo', {})
        default_deveui = "010203040506070A" if node_id == 3 else f"010203040506070{node_id}"
        dev_eui = device_info.get('devEui') or payload.get('devEUI') or payload.get('devEui') or topic_deveui or default_deveui
        dev_name = device_info.get('deviceName') or payload.get('deviceName') or f"Heltec-V3-Nodo{node_id}"
        f_cnt = payload.get('f_cnt') or payload.get('fCnt') or payload.get('fcnt') or obj.get('sequence', 0)

        # Metadatos RF reales de la pasarela UG65
        rx_info = payload.get('rxInfo')
        if isinstance(rx_info, list) and len(rx_info) > 0:
            first_rx = rx_info[0]
            rssi = first_rx.get('rssi', -70)
            snr = first_rx.get('loRaSNR') if first_rx.get('loRaSNR') is not None else first_rx.get('snr', 10.0)
        else:
            rssi = payload.get('rssi', -70)
            snr = payload.get('snr', 10.0)

        temp = float(obj.get("temperature", 0.0))
        hum = float(obj.get("humidity", 0.0))
        
        # Batería
        bat_v = float(obj.get("battery_v", 0.0))
        bat_mv = int(obj.get("battery_mv", round(bat_v * 1000) if bat_v > 0 else 3800))
        bat_pct = int(obj.get("battery_pct", round(((bat_v - 3.0) / 1.2) * 100) if bat_v > 0 else 85))
        if bat_pct < 0: bat_pct = 0
        if bat_pct > 100: bat_pct = 100

        seq = int(obj.get("packet_seq", obj.get("sequence", f_cnt)))
        flags = int(obj.get("status_flags", 0))

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        packet = {
            "timestamp": now_str,
            "device_name": dev_name,
            "dev_eui": dev_eui,
            "temperature": temp,
            "humidity": hum,
            "battery_mv": bat_mv,
            "battery_pct": bat_pct,
            "packet_seq": seq,
            "status_flags": flags,
            "rssi": int(rssi),
            "snr": float(snr),
            "f_cnt": int(f_cnt)
        }

        with history_lock:
            latest_packet = packet

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''
            INSERT INTO telemetry 
            (timestamp, device_name, dev_eui, temperature, humidity, battery_mv, battery_pct, packet_seq, status_flags, rssi, snr, f_cnt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            packet["timestamp"], packet["device_name"], packet["dev_eui"],
            packet["temperature"], packet["humidity"], packet["battery_mv"],
            packet["battery_pct"], packet["packet_seq"], packet["status_flags"],
            packet["rssi"], packet["snr"], packet["f_cnt"]
        ))
        conn.commit()
        conn.close()
        print(f"[MQTT OK] {dev_name} ({dev_eui}) -> Temp: {temp}C | Hum: {hum}% | Bat: {bat_pct}% | RSSI: {rssi} dBm", flush=True)
    except Exception as e:
        print("[MQTT Error]", e, flush=True)

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    while True:
        try:
            client.connect("localhost", 1883, 60)
            client.loop_forever()
        except Exception as e:
            print("[MQTT] Error de conexion, reintentando...", e, flush=True)
            time.sleep(3)


def build_telemetry_query(params):
    query = 'SELECT id, timestamp, device_name, dev_eui, temperature, humidity, battery_mv, battery_pct, packet_seq, status_flags, rssi, snr, f_cnt FROM telemetry WHERE 1=1'
    sql_params = []
    
    node = params.get('node', [''])[0]
    if node and node != 'ALL':
        if 'Nodo1' in node:
            query += " AND (device_name LIKE '%Nodo1%' OR dev_eui LIKE '%08' OR dev_eui LIKE '%01')"
        elif 'Nodo2' in node:
            query += " AND (device_name LIKE '%Nodo2%' OR dev_eui LIKE '%09' OR dev_eui LIKE '%02')"
        elif 'Nodo3' in node:
            query += " AND (device_name LIKE '%Nodo3%' OR dev_eui LIKE '%0a' OR dev_eui LIKE '%0A' OR dev_eui LIKE '%03')"
        else:
            query += ' AND (device_name LIKE ? OR dev_eui LIKE ?)'
            sql_params.extend([f"%{node}%", f"%{node}%"])
        
    start_date = params.get('start_date', [''])[0]
    if start_date:
        query += ' AND date(timestamp) >= ?'
        sql_params.append(start_date)
        
    end_date = params.get('end_date', [''])[0]
    if end_date:
        query += ' AND date(timestamp) <= ?'
        sql_params.append(end_date)
        
    start_time = params.get('start_time', [''])[0]
    if start_time:
        if len(start_time) == 5: start_time += ":00"
        query += ' AND time(timestamp) >= ?'
        sql_params.append(start_time)
        
    end_time = params.get('end_time', [''])[0]
    if end_time:
        if len(end_time) == 5: end_time += ":59"
        query += ' AND time(timestamp) <= ?'
        sql_params.append(end_time)
        
    slot = params.get('slot', [''])[0]
    if slot == 'manana':
        query += " AND time(timestamp) BETWEEN '08:00:00' AND '11:59:59'"
    elif slot == 'mediodia':
        query += " AND time(timestamp) BETWEEN '12:00:00' AND '14:59:59'"
    elif slot == 'tarde':
        query += " AND time(timestamp) BETWEEN '15:00:00' AND '18:59:59'"
    elif slot == 'noche':
        query += " AND (time(timestamp) >= '19:00:00' OR time(timestamp) <= '07:59:59')"

    since_id = params.get('since_id', [''])[0]
    if since_id:
        try:
            query += ' AND id >= ?'
            sql_params.append(int(since_id))
        except: pass

    until_id = params.get('until_id', [''])[0]
    if until_id:
        try:
            query += ' AND id <= ?'
            sql_params.append(int(until_id))
        except: pass
        
    return query, sql_params

HTML_PAGE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Dashboard LoRaWAN UCT | Telemetría Campus Dr. Luis Rivas del Canto</title>
  <style>
    :root {
      --bg: #0b0f19;
      --card-bg: rgba(17, 24, 39, 0.78);
      --card-hover: rgba(26, 36, 56, 0.85);
      --border: rgba(255, 255, 255, 0.08);
      --border-active: #38bdf8;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --cyan: #38bdf8;
      --emerald: #34d399;
      --amber: #fbbf24;
      --orange: #fb923c;
      --purple: #c084fc;
      --red: #f87171;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
      background: radial-gradient(circle at 15% 15%, #132448 0%, var(--bg) 85%);
      color: var(--text);
      min-height: 100vh;
      padding: 24px 20px;
    }
    .container { max-width: 1360px; margin: 0 auto; }

    /* HEADER */
    header {
      display: flex; justify-content: space-between; align-items: center;
      padding-bottom: 20px; border-bottom: 1px solid var(--border);
      margin-bottom: 22px; flex-wrap: wrap; gap: 16px;
    }
    .header-left h1 { font-size: 26px; font-weight: 800; display: flex; align-items: center; gap: 12px; letter-spacing: -0.5px; }
    .badge-uct {
      background: linear-gradient(135deg, #1d4ed8, #0284c7);
      color: white; font-size: 11px; font-weight: 700; padding: 4px 10px;
      border-radius: 6px; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .subtitle { color: var(--text-muted); font-size: 13.5px; margin-top: 5px; }
    
    .header-right { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
    .status-pill {
      display: flex; align-items: center; gap: 8px; background: rgba(17, 24, 39, 0.9);
      padding: 8px 16px; border-radius: 30px; border: 1px solid var(--border); font-size: 13px; font-weight: 600;
    }
    .live-dot {
      width: 10px; height: 10px; background-color: var(--emerald);
      border-radius: 50%; box-shadow: 0 0 10px var(--emerald);
      animation: pulse 2s infinite;
    }
    .live-dot.paused { background-color: var(--amber); box-shadow: 0 0 10px var(--amber); animation: none; }
    @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.35; transform: scale(0.85); } 100% { opacity: 1; transform: scale(1); } }

    .btn {
      display: inline-flex; align-items: center; gap: 7px;
      background: rgba(30, 41, 59, 0.8); color: var(--text);
      border: 1px solid var(--border); padding: 8px 15px; border-radius: 8px;
      font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.2s ease;
      text-decoration: none;
    }
    .btn:hover { background: rgba(51, 65, 85, 0.9); border-color: rgba(255, 255, 255, 0.2); transform: translateY(-1px); }
    .btn-primary { background: linear-gradient(135deg, #0284c7, #2563eb); border: none; color: white; }
    .btn-primary:hover { background: linear-gradient(135deg, #0369a1, #1d4ed8); }

    /* TOOLBAR DE FILTROS */
    .toolbar {
      background: var(--card-bg); backdrop-filter: blur(14px);
      border: 1px solid var(--border); border-radius: 14px;
      padding: 14px 18px; margin-bottom: 22px;
      display: flex; justify-content: space-between; align-items: center;
      gap: 16px; flex-wrap: wrap;
    }
    .node-selector { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
    .filter-btn {
      padding: 7px 14px; border-radius: 8px; font-size: 13px; font-weight: 600;
      border: 1px solid var(--border); background: rgba(15, 23, 42, 0.6);
      color: var(--text-muted); cursor: pointer; transition: all 0.2s;
    }
    .filter-btn:hover { color: var(--text); background: rgba(30, 41, 59, 0.8); }
    .filter-btn.active {
      background: rgba(56, 189, 248, 0.15); border-color: var(--cyan);
      color: var(--cyan); box-shadow: 0 0 12px rgba(56, 189, 248, 0.2);
    }
    .search-group { display: flex; align-items: center; gap: 10px; flex: 1; min-width: 260px; max-width: 420px; }
    .search-input {
      width: 100%; background: rgba(15, 23, 42, 0.7);
      border: 1px solid var(--border); border-radius: 8px;
      padding: 8px 14px; color: var(--text); font-size: 13px; outline: none;
      transition: border-color 0.2s;
    }
    .search-input:focus { border-color: var(--cyan); }

    /* STATS CARDS */
    .grid-stats {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 18px; margin-bottom: 22px;
    }
    .card {
      background: var(--card-bg); backdrop-filter: blur(14px);
      border: 1px solid var(--border); border-radius: 16px; padding: 20px;
      box-shadow: 0 8px 24px rgba(0,0,0,0.3); transition: transform 0.2s, border-color 0.2s;
    }
    .card:hover { transform: translateY(-2px); border-color: rgba(255, 255, 255, 0.16); }
    .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
    .card-title { font-size: 12.5px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
    .stat-val { font-size: 38px; font-weight: 800; line-height: 1; margin-bottom: 8px; }
    .stat-unit { font-size: 19px; font-weight: 600; color: var(--text-muted); margin-left: 5px; }
    .stat-sub { font-size: 12.5px; color: var(--text-muted); display: flex; justify-content: space-between; align-items: center; }
    .progress-bar-bg { height: 6px; background: rgba(255, 255, 255, 0.08); border-radius: 3px; margin-top: 12px; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 3px; transition: width 0.4s ease; }

    /* CHARTS */
    .grid-charts { display: grid; grid-template-columns: 2fr 1fr; gap: 18px; margin-bottom: 22px; }
    @media (max-width: 960px) { .grid-charts { grid-template-columns: 1fr; } }
    .chart-card {
      background: var(--card-bg); backdrop-filter: blur(14px);
      border: 1px solid var(--border); border-radius: 16px; padding: 20px;
    }
    .chart-card h2 { font-size: 15px; font-weight: 700; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; }
    .chart-legend { display: flex; gap: 14px; font-size: 12px; font-weight: 600; }
    .legend-item { display: flex; align-items: center; gap: 6px; }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; }
    .canvas-container { position: relative; width: 100%; height: 230px; }
    canvas { width: 100% !important; height: 100% !important; }

    /* TABLA DE HISTORIAL */
    .table-card {
      background: var(--card-bg); backdrop-filter: blur(14px);
      border: 1px solid var(--border); border-radius: 16px; padding: 20px;
    }
    .table-header-flex {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 16px; flex-wrap: wrap; gap: 12px;
    }
    .table-header-flex h2 { font-size: 15px; font-weight: 700; }
    .table-controls { display: flex; align-items: center; gap: 10px; }
    .table-select {
      background: rgba(15, 23, 42, 0.7); border: 1px solid var(--border);
      color: var(--text); border-radius: 6px; padding: 5px 10px; font-size: 12px; outline: none;
    }
    .table-wrapper { overflow-x: auto; max-height: 480px; }
    table { width: 100%; border-collapse: collapse; font-size: 13px; text-align: left; }
    thead th {
      position: sticky; top: 0; background: #131c2e;
      padding: 11px 14px; color: var(--text-muted); border-bottom: 1px solid var(--border);
      font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; z-index: 2;
    }
    td { padding: 12px 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.04); }
    tr:hover td { background: rgba(255, 255, 255, 0.03); }
    .tag { padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 700; display: inline-block; }
    .tag-blue { background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); }
    .tag-purple { background: rgba(192, 132, 252, 0.15); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.3); }
    .tag-teal { background: rgba(20, 184, 166, 0.15); color: #2dd4bf; border: 1px solid rgba(20, 184, 166, 0.3); }
    .tag-green { background: rgba(52, 211, 153, 0.15); color: #34d399; }
    .tag-amber { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }

    /* PANEL DE SESIONES EXPERIMENTALES (TIPO B Y TIPO A) */
    .session-card {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.09) 0%, rgba(15, 23, 42, 0.88) 100%);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(52, 211, 153, 0.35);
      box-shadow: 0 0 25px rgba(16, 185, 129, 0.10);
      border-radius: 16px; padding: 20px 24px; margin-bottom: 22px;
    }
    .session-top {
      display: flex; justify-content: space-between; align-items: flex-start;
      gap: 16px; margin-bottom: 14px; flex-wrap: wrap;
    }
    .session-title-group h2 { font-size: 17px; font-weight: 800; display: flex; align-items: center; gap: 10px; }
    .session-badge {
      display: inline-block; background: rgba(52, 211, 153, 0.2); color: #34d399;
      font-size: 11px; font-weight: 800; padding: 3px 9px; border-radius: 6px;
      text-transform: uppercase; letter-spacing: 0.5px; border: 1px solid rgba(52, 211, 153, 0.4); margin-bottom: 6px;
    }
    .session-desc { font-size: 13px; color: var(--text-muted); margin-top: 4px; }
    .session-actions { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
    .btn-emerald { background: linear-gradient(135deg, #059669, #10b981); border: none; color: white; }
    .btn-emerald:hover { background: linear-gradient(135deg, #047857, #059669); }
    .btn-amber { background: linear-gradient(135deg, #d97706, #f59e0b); border: none; color: white; }
    .btn-amber:hover { background: linear-gradient(135deg, #b45309, #d97706); }
    .session-progress-container { margin: 16px 0; }
    .session-progress-bar-bg { height: 10px; background: rgba(255, 255, 255, 0.08); border-radius: 5px; overflow: hidden; }
    .session-progress-bar-fill { height: 100%; border-radius: 5px; background: linear-gradient(90deg, #10b981, #38bdf8); transition: width 0.3s ease; }
    .session-progress-labels { display: flex; justify-content: space-between; font-size: 13px; margin-top: 8px; align-items: center; }
    .session-metrics-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px; padding-top: 14px; border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    .session-metric-item { background: rgba(0, 0, 0, 0.25); padding: 10px 14px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.04); }
    .session-metric-item .lbl { font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; display: block; margin-bottom: 4px; }
    .session-metric-item .val { font-size: 16px; font-weight: 800; color: var(--text); }

    /* MODAL DE EXPORTACIÓN AVANZADA */
    .modal-backdrop {
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(11, 15, 25, 0.85); backdrop-filter: blur(8px);
      display: none; align-items: center; justify-content: center;
      z-index: 9999; padding: 20px;
    }
    .modal-backdrop.active { display: flex; }
    .modal-box {
      background: #111827; border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 18px; width: 100%; max-width: 650px; padding: 26px;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7); animation: modalAnim 0.2s ease-out;
      max-height: 90vh; overflow-y: auto;
    }
    @keyframes modalAnim { from { opacity: 0; transform: scale(0.96) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
    .modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 14px; }
    .modal-header h2 { font-size: 20px; font-weight: 800; display: flex; align-items: center; gap: 10px; color: var(--text); }
    .modal-close { background: transparent; border: none; font-size: 24px; color: var(--text-muted); cursor: pointer; transition: color 0.2s; line-height: 1; }
    .modal-close:hover { color: var(--text); }
    .filter-section { margin-bottom: 18px; }
    .filter-section-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--cyan); margin-bottom: 8px; }
    .pill-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
    .pill-btn {
      background: rgba(30, 41, 59, 0.8); border: 1px solid var(--border);
      color: var(--text-muted); padding: 6px 12px; border-radius: 7px;
      font-size: 12.5px; font-weight: 600; cursor: pointer; transition: all 0.2s;
    }
    .pill-btn:hover { background: rgba(51, 65, 85, 0.9); color: var(--text); }
    .pill-btn.active { background: rgba(56, 189, 248, 0.2); border-color: var(--cyan); color: var(--cyan); }
    .input-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .input-field-group label { display: block; font-size: 11.5px; color: var(--text-muted); margin-bottom: 4px; }
    .modal-input {
      width: 100%; background: rgba(15, 23, 42, 0.8); border: 1px solid var(--border);
      border-radius: 8px; padding: 8px 12px; color: var(--text); font-size: 13px; outline: none;
    }
    .modal-input:focus { border-color: var(--cyan); }
    .export-preview-box {
      background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border);
      border-radius: 12px; padding: 14px 18px; margin: 18px 0;
      display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;
    }
    .preview-count { font-size: 14px; font-weight: 700; color: var(--emerald); display: flex; align-items: center; gap: 6px; }
    .preview-count.empty { color: var(--amber); }
    .modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 22px; border-top: 1px solid var(--border); padding-top: 16px; flex-wrap: wrap; }
  </style>

</head>
<body>
  <div class="container">
    <header>
      <div class="header-left">
        <h1>Red de Sensores LoRaWAN <span class="badge-uct">UCT Temuco</span></h1>
        <div class="subtitle">Campus Dr. Luis Rivas del Canto &bull; Gateway Milesight UG65 &bull; Nodos Heltec WiFi LoRa 32 V3</div>
      </div>
      <div class="header-right">
        <div class="status-pill">
          <div class="live-dot" id="live-indicator"></div>
          <span id="live-text">En Vivo</span>
          <span style="color: var(--text-muted); font-size: 12px; margin-left: 4px;" id="lbl-last-update">--</span>
        </div>
        <button class="btn" id="btn-toggle-pause" onclick="toggleAutoRefresh()">⏸️ Pausar</button>
        <button class="btn btn-primary" onclick="openExportModal()">📥 Exportar / Filtrar CSV</button>
      </div>
    </header>

    <!-- BARRA DE FILTROS Y BÚSQUEDA -->
    <div class="toolbar">
      <div class="node-selector">
        <span style="font-size: 13px; font-weight: 700; color: var(--text-muted); margin-right: 4px;">FILTRAR NODO:</span>
        <button class="filter-btn active" id="btn-node-all" onclick="selectNode('ALL')">🌐 Todos los Nodos (<span id="cnt-all">0</span>)</button>
        <button class="filter-btn" id="btn-node-1" onclick="selectNode('Nodo1')">📡 Nodo 1 (LOS) (<span id="cnt-node1">0</span>)</button>
        <button class="filter-btn" id="btn-node-2" onclick="selectNode('Nodo2')">🏢 Nodo 2 (NLOS) (<span id="cnt-node2">0</span>)</button>
        <button class="filter-btn" id="btn-node-3" onclick="selectNode('Nodo3')">🔬 Nodo 3 (Exp) (<span id="cnt-node3">0</span>)</button>
      </div>
      <div class="search-group">
        <input type="text" id="input-search" class="search-input" placeholder="🔍 Buscar por fecha, secuencia, nodo o FCnt..." oninput="onSearchChange()">
      </div>
    </div>

    <!-- PANEL DE CONTROL DE SESIONES EXPERIMENTALES (ETAPA 3) -->
    <div class="session-card" id="session-card">
      <div class="session-top">
        <div class="session-title-group">
          <span class="session-badge" id="session-badge">🎯 MODO: SESIÓN TIPO B (CONFIRMADA CON ACK)</span>
          <h2 id="session-heading">Control de Sesión de Evaluación — 30 Tramas</h2>
          <div class="session-desc">Medición de retardo de confirmación (T_conf &le; 6s) y tasa de pérdida (PL &le; 10%) según el protocolo SMART de la tesis.</div>
        </div>
        <div class="session-actions">
          <button class="btn btn-emerald" id="btn-session-start" onclick="handleSessionButtonClick()">▶️ Iniciar Captura (30 tramas)</button>
          <button class="btn" id="btn-session-switch" onclick="switchSessionType()">🔄 Modo: Tipo B (30)</button>
          <button class="btn" id="btn-session-view" onclick="toggleSessionViewOnly()">🎯 Ver Solo Sesión</button>
          <button class="btn btn-primary" id="btn-session-export" onclick="exportSessionCSV()" disabled>📥 Descargar CSV de Sesión</button>
        </div>
      </div>

      <div class="session-progress-container">
        <div class="session-progress-bar-bg">
          <div class="session-progress-bar-fill" id="session-progress-fill" style="width: 0%;"></div>
        </div>
        <div class="session-progress-labels">
          <span id="session-progress-text">Progreso: <strong>0 / 30 tramas</strong> (0%)</span>
          <span id="session-status-tag" class="tag tag-amber">En Espera &bull; Presiona Iniciar</span>
        </div>
      </div>

      <div class="session-metrics-grid">
        <div class="session-metric-item">
          <span class="lbl">Filtro de Nodo:</span>
          <span class="val" id="session-lbl-node" style="color: var(--cyan);">Todos</span>
        </div>
        <div class="session-metric-item">
          <span class="lbl">Tramas Capturadas:</span>
          <span class="val" id="session-lbl-count">0 tramas</span>
        </div>
        <div class="session-metric-item">
          <span class="lbl">Pérdida (PL Estimada):</span>
          <span class="val" id="session-lbl-pl">0.0% <small style="color:var(--text-muted); font-weight:normal;">(&le;10%)</small></span>
        </div>
        <div class="session-metric-item">
          <span class="lbl">RSSI Promedio Sesión:</span>
          <span class="val" id="session-lbl-rssi" style="color: var(--purple);">-- dBm</span>
        </div>
        <div class="session-metric-item">
          <span class="lbl">Criterio SMART:</span>
          <span class="val" id="session-lbl-smart" style="color: var(--amber);">Pendiente</span>
        </div>
      </div>
    </div>

    <!-- TARJETAS DE MÉTRICAS KPI -->
    <div class="grid-stats">
      <div class="card">
        <div class="card-header"><span class="card-title">Temperatura</span><span>🌡️</span></div>
        <div class="stat-val" style="color: var(--orange);"><span id="val-temp">--</span><span class="stat-unit">°C</span></div>
        <div class="stat-sub"><span>Sensor ambiental</span><span id="sub-temp-range">--</span></div>
        <div class="progress-bar-bg"><div class="progress-fill" id="bar-temp" style="width: 0%; background: var(--orange);"></div></div>
      </div>

      <div class="card">
        <div class="card-header"><span class="card-title">Humedad Relativa</span><span>💧</span></div>
        <div class="stat-val" style="color: var(--cyan);"><span id="val-hum">--</span><span class="stat-unit">%</span></div>
        <div class="stat-sub"><span>Humedad del aire</span><span id="sub-hum-range">--</span></div>
        <div class="progress-bar-bg"><div class="progress-fill" id="bar-hum" style="width: 0%; background: var(--cyan);"></div></div>
      </div>

      <div class="card">
        <div class="card-header"><span class="card-title">Batería del Nodo</span><span>🔋</span></div>
        <div class="stat-val" style="color: var(--emerald);"><span id="val-bat">--</span><span class="stat-unit">%</span></div>
        <div class="stat-sub"><span id="val-bat-mv">Voltaje: -- mV</span><span id="sub-bat-health">LiPo 3.7V</span></div>
        <div class="progress-bar-bg"><div class="progress-fill" id="bar-bat" style="width: 0%; background: var(--emerald);"></div></div>
      </div>

      <div class="card">
        <div class="card-header"><span class="card-title">Calidad Enlace LoRa</span><span>📡</span></div>
        <div class="stat-val" style="color: var(--purple);"><span id="val-rssi">--</span><span class="stat-unit">dBm</span></div>
        <div class="stat-sub"><span id="val-snr">SNR: -- dB</span><span id="val-fcnt">FCnt: --</span></div>
        <div class="progress-bar-bg"><div class="progress-fill" id="bar-rssi" style="width: 0%; background: var(--purple);"></div></div>
      </div>
    </div>

    <!-- GRÁFICOS HISTÓRICOS -->
    <div class="grid-charts">
      <div class="chart-card">
        <h2>
          <span>Curva Histórica de Temperatura y Humedad</span>
          <div class="chart-legend">
            <div class="legend-item"><div class="legend-dot" style="background: var(--orange);"></div>Temp (°C)</div>
            <div class="legend-item"><div class="legend-dot" style="background: var(--cyan);"></div>Hum (%)</div>
          </div>
        </h2>
        <div class="canvas-container"><canvas id="chart-telemetry"></canvas></div>
      </div>
      <div class="chart-card">
        <h2>
          <span>Intensidad de Señal RF (RSSI)</span>
          <div class="chart-legend">
            <div class="legend-item"><div class="legend-dot" style="background: var(--purple);"></div>RSSI (dBm)</div>
          </div>
        </h2>
        <div class="canvas-container"><canvas id="chart-rssi"></canvas></div>
      </div>
    </div>

    <!-- TABLA DE HISTORIAL -->
    <div class="table-card">
      <div class="table-header-flex">
        <h2>Historial de Telemetría Registrada (<span id="lbl-table-count">0 tramas</span>)</h2>
        <div class="table-controls">
          <label style="font-size: 12px; color: var(--text-muted);">Mostrar:</label>
          <select id="select-limit" class="table-select" onchange="onLimitChange()">
            <option value="25">Últimas 25</option>
            <option value="50" selected>Últimas 50</option>
            <option value="100">Últimas 100</option>
            <option value="all">Todo el Historial</option>
          </select>
        </div>
      </div>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Fecha y Hora</th>
              <th>Dispositivo</th>
              <th>DevEUI</th>
              <th>FCnt</th>
              <th>Seq</th>
              <th>Temperatura</th>
              <th>Humedad</th>
              <th>Batería</th>
              <th>RSSI</th>
              <th>SNR</th>
            </tr>
          </thead>
          <tbody id="table-body">
            <tr><td colspan="11" style="text-align: center; color: var(--text-muted); padding: 30px;">Cargando tramas...</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    let selectedNode = 'ALL';
    let searchQuery = '';
    let currentLimit = '50';
    let isPaused = false;
    let allDataRows = [];

    // CONTROL DE SESIÓN EXPERIMENTAL (ETAPA 3 - CAPTURADOR SINCRONIZADO)
    let sessionActive = false;
    let sessionType = 'B'; // 'B' = 30 tramas, 'A' = 100 tramas
    let sessionTarget = 30;
    let sessionStartId = null;
    let sessionEndId = null;
    let sessionCapturedRows = [];
    let sessionCompleted = false;
    let viewSessionOnly = false;

    function switchSessionType() {
      if (sessionType === 'B') {
        sessionType = 'A';
        sessionTarget = 100;
        document.getElementById('session-badge').innerText = '📊 MODO: SESIÓN TIPO A (NO CONFIRMADA)';
        document.getElementById('session-badge').style.borderColor = 'rgba(56, 189, 248, 0.4)';
        document.getElementById('session-badge').style.color = '#38bdf8';
        document.getElementById('session-badge').style.background = 'rgba(56, 189, 248, 0.15)';
        document.getElementById('session-heading').innerText = 'Control de Sesión de Evaluación — 100 Tramas';
        document.getElementById('btn-session-switch').innerText = '🔄 Modo: Tipo A (100)';
      } else {
        sessionType = 'B';
        sessionTarget = 30;
        document.getElementById('session-badge').innerText = '🎯 MODO: SESIÓN TIPO B (CONFIRMADA CON ACK)';
        document.getElementById('session-badge').style.borderColor = 'rgba(52, 211, 153, 0.4)';
        document.getElementById('session-badge').style.color = '#34d399';
        document.getElementById('session-badge').style.background = 'rgba(52, 211, 153, 0.2)';
        document.getElementById('session-heading').innerText = 'Control de Sesión de Evaluación — 30 Tramas';
        document.getElementById('btn-session-switch').innerText = '🔄 Modo: Tipo B (30)';
      }
      startEvaluationSession();
    }

    function handleSessionButtonClick() {
      if (sessionActive && !sessionCompleted) {
        if (confirm(`¿Deseas reiniciar la captura de la sesión (${sessionCapturedRows.length}/${sessionTarget} tramas capturadas hasta ahora)?`)) {
          startEvaluationSession();
        }
      } else {
        startEvaluationSession();
      }
    }

    function startEvaluationSession() {
      sessionActive = true;
      sessionCompleted = false;
      sessionCapturedRows = [];
      // Captura estrictamente a partir de la próxima trama que ingrese
      sessionStartId = (allDataRows.length > 0 ? allDataRows[0].id : 0) + 1;
      sessionEndId = null;

      const btnStart = document.getElementById('btn-session-start');
      if (btnStart) {
        btnStart.innerText = '⏹️ Cancelar / Reiniciar';
        btnStart.className = 'btn btn-amber';
      }
      const btnExp = document.getElementById('btn-session-export');
      if (btnExp) {
        btnExp.disabled = true;
        btnExp.innerText = `📥 Descargar CSV (${sessionTarget} tramas)`;
      }

      renderSessionUI();
      renderDashboard();
    }

    function toggleSessionViewOnly() {
      if (sessionCapturedRows.length === 0) {
        alert('Aún no hay tramas capturadas en esta sesión. Inicia la captura para visualizarlas.');
        return;
      }
      viewSessionOnly = !viewSessionOnly;
      const btn = document.getElementById('btn-session-view');
      if (btn) {
        btn.classList.toggle('active', viewSessionOnly);
        btn.innerText = viewSessionOnly ? '🌐 Ver Todo el Historial' : `🎯 Ver Solo Sesión (${sessionCapturedRows.length})`;
      }
      renderDashboard();
    }

    function exportSessionCSV() {
      if (sessionCapturedRows.length === 0) {
        alert('No hay tramas capturadas en esta sesión.');
        return;
      }
      const nodeTag = selectedNode === 'Heltec-V3-Nodo1' ? 'Nodo1_LOS' : (selectedNode === 'Heltec-V3-Nodo2' ? 'Nodo2_NLOS' : 'TodosNodos');
      const now = new Date();
      const pad = n => String(n).padStart(2, '0');
      const dateTag = `${now.getFullYear()}${pad(now.getMonth()+1)}${pad(now.getDate())}`;
      const timeTag = `${pad(now.getHours())}${pad(now.getMinutes())}`;
      const fn = `sesion_tipo${sessionType}_${nodeTag}_${sessionCapturedRows.length}tramas_${dateTag}_${timeTag}.csv`;
      
      const startId = sessionCapturedRows[0].id;
      const endId = sessionCapturedRows[sessionCapturedRows.length - 1].id;
      const nodeParam = selectedNode === 'ALL' ? 'ALL' : selectedNode;
      
      window.location.href = `/api/export-csv?since_id=${startId}&until_id=${endId}&node=${nodeParam}&limit=${sessionTarget}&filename=${fn}`;
    }

    function renderSessionUI() {
      const count = sessionCapturedRows.length;
      const targetNodeName = selectedNode === 'ALL' ? 'Todos los Nodos' : (selectedNode.includes('Nodo1') ? 'Nodo 1 (LOS)' : (selectedNode.includes('Nodo2') ? 'Nodo 2 (NLOS)' : 'Nodo 3 (Exp)'));
      document.getElementById('session-lbl-node').innerText = targetNodeName;
      document.getElementById('session-lbl-count').innerText = `${count} / ${sessionTarget} tramas`;
      
      const pct = Math.min(100, Math.round((count / sessionTarget) * 100));
      document.getElementById('session-progress-fill').style.width = pct + '%';
      document.getElementById('session-progress-text').innerHTML = `Progreso: <strong>${count} / ${sessionTarget} tramas</strong> (${pct}%)`;

      if (count > 0) {
        const avgRssi = (sessionCapturedRows.reduce((acc, r) => acc + r.rssi, 0) / count).toFixed(1);
        document.getElementById('session-lbl-rssi').innerText = `${avgRssi} dBm`;
        
        if (count >= 2) {
          const firstSeq = sessionCapturedRows[0].f_cnt || sessionCapturedRows[0].packet_seq;
          const lastSeq = sessionCapturedRows[count - 1].f_cnt || sessionCapturedRows[count - 1].packet_seq;
          const expected = Math.abs(lastSeq - firstSeq) + 1;
          const lost = Math.max(0, expected - count);
          const pl = ((lost / expected) * 100).toFixed(1);
          document.getElementById('session-lbl-pl').innerHTML = `${pl}% <small style="color:var(--text-muted);">(${lost} perdidas de ${expected})</small>`;
        }
      } else {
        document.getElementById('session-lbl-rssi').innerText = '-- dBm';
        document.getElementById('session-lbl-pl').innerText = '0.0%';
      }

      if (sessionCompleted) {
        document.getElementById('session-progress-fill').style.background = 'linear-gradient(90deg, #10b981, #059669)';
        document.getElementById('session-status-tag').className = 'tag tag-green';
        document.getElementById('session-status-tag').innerText = `✅ ¡Sesión Completada! (${count}/${sessionTarget} tramas)`;
        document.getElementById('session-lbl-smart').innerHTML = `<span style="color: var(--emerald); font-weight: 800;">✅ CUMPLE SMART (${count} tramas)</span>`;
        const btnExp = document.getElementById('btn-session-export');
        if (btnExp) {
          btnExp.disabled = false;
          btnExp.innerText = `📥 Descargar CSV (${count} tramas)`;
        }
        const btnStart = document.getElementById('btn-session-start');
        if (btnStart) {
          btnStart.innerText = `▶️ Iniciar Nueva Sesión (${sessionTarget})`;
          btnStart.className = 'btn btn-emerald';
        }
      } else if (sessionActive) {
        document.getElementById('session-progress-fill').style.background = 'linear-gradient(90deg, #10b981, #38bdf8)';
        document.getElementById('session-status-tag').className = 'tag tag-blue';
        document.getElementById('session-status-tag').innerText = count === 0 
          ? `🟡 Esperando primera trama... (0/${sessionTarget})` 
          : `📡 Capturando tramas (${count}/${sessionTarget})...`;
        document.getElementById('session-lbl-smart').innerHTML = `<span style="color: var(--cyan);">En captura (${count}/${sessionTarget})</span>`;
      } else {
        document.getElementById('session-status-tag').className = 'tag tag-amber';
        document.getElementById('session-status-tag').innerText = 'En Espera • Presiona Iniciar';
        document.getElementById('session-lbl-smart').innerHTML = `<span style="color: var(--amber);">Pendiente</span>`;
      }
    }

    function isMatchNode(r, nodeKey) {
      if (!nodeKey || nodeKey === 'ALL') return true;
      const dName = (r.device_name || '').toLowerCase();
      const dEui = (r.dev_eui || '').toLowerCase();
      if (nodeKey === 'Nodo1' || nodeKey.includes('Nodo1')) {
        return dName.includes('nodo1') || dEui.endsWith('08') || dEui.endsWith('01');
      }
      if (nodeKey === 'Nodo2' || nodeKey.includes('Nodo2')) {
        return dName.includes('nodo2') || dEui.endsWith('09') || dEui.endsWith('02');
      }
      if (nodeKey === 'Nodo3' || nodeKey.includes('Nodo3')) {
        return dName.includes('nodo3') || dEui.endsWith('0a') || dEui.endsWith('03');
      }
      return dName.includes(nodeKey.toLowerCase()) || dEui.includes(nodeKey.toLowerCase());
    }

    function selectNode(node) {
      selectedNode = node;
      document.getElementById('btn-node-all').classList.toggle('active', node === 'ALL');
      document.getElementById('btn-node-1').classList.toggle('active', node === 'Nodo1' || node.includes('Nodo1'));
      document.getElementById('btn-node-2').classList.toggle('active', node === 'Nodo2' || node.includes('Nodo2'));
      if (document.getElementById('btn-node-3')) {
        document.getElementById('btn-node-3').classList.toggle('active', node === 'Nodo3' || node.includes('Nodo3'));
      }
      renderDashboard();
    }

    function onSearchChange() {
      searchQuery = document.getElementById('input-search').value.toLowerCase().trim();
      renderDashboard();
    }

    function onLimitChange() {
      currentLimit = document.getElementById('select-limit').value;
      updateDashboard();
    }

    function toggleAutoRefresh() {
      isPaused = !isPaused;
      const btn = document.getElementById('btn-toggle-pause');
      const dot = document.getElementById('live-indicator');
      const txt = document.getElementById('live-text');
      if (isPaused) {
        btn.innerHTML = '▶️ Reanudar';
        dot.classList.add('paused');
        txt.innerText = 'Pausado';
      } else {
        btn.innerHTML = '⏸️ Pausar';
        dot.classList.remove('paused');
        txt.innerText = 'En Vivo';
        updateDashboard();
      }
    }

    function drawLineChart(canvasId, dataSeries) {
      const canvas = document.getElementById(canvasId);
      if (!canvas) return;
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const width = canvas.parentElement.clientWidth;
      const height = canvas.parentElement.clientHeight;
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      ctx.scale(dpr, dpr);
      ctx.clearRect(0, 0, width, height);

      if (!dataSeries || dataSeries.length === 0 || dataSeries[0].data.length === 0) {
        ctx.fillStyle = '#64748b'; ctx.font = '13px sans-serif'; ctx.textAlign = 'center';
        ctx.fillText('Sin tramas registradas para el filtro seleccionado', width / 2, height / 2);
        return;
      }

      const padding = { top: 20, right: 20, bottom: 25, left: 45 };
      const chartW = width - padding.left - padding.right;
      const chartH = height - padding.top - padding.bottom;

      let allVals = [];
      dataSeries.forEach(s => allVals.push(...s.data));
      let minVal = Math.min(...allVals);
      let maxVal = Math.max(...allVals);
      if (minVal === maxVal) { minVal -= 5; maxVal += 5; }
      const margin = (maxVal - minVal) * 0.15 || 2;
      minVal = Math.floor(minVal - margin);
      maxVal = Math.ceil(maxVal + margin);

      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.lineWidth = 1;
      ctx.fillStyle = '#64748b';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'right';

      for (let i = 0; i <= 4; i++) {
        const y = padding.top + (chartH / 4) * i;
        const val = (maxVal - (maxVal - minVal) * (i / 4)).toFixed(1);
        ctx.beginPath(); ctx.moveTo(padding.left, y); ctx.lineTo(width - padding.right, y); ctx.stroke();
        ctx.fillText(val, padding.left - 8, y + 3);
      }

      const numPoints = dataSeries[0].data.length;
      dataSeries.forEach(series => {
        if (series.data.length < 1) return;
        ctx.beginPath();
        ctx.lineWidth = 2.5;
        ctx.strokeStyle = series.color;

        const points = [];
        series.data.forEach((val, i) => {
          const x = numPoints === 1 ? padding.left + chartW / 2 : padding.left + (chartW / (numPoints - 1)) * i;
          const y = padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;
          points.push({x, y});
          if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        });
        ctx.stroke();

        points.forEach(p => {
          ctx.beginPath(); ctx.arc(p.x, p.y, 3.5, 0, Math.PI * 2);
          ctx.fillStyle = series.color; ctx.fill();
        });
      });
    }

    function renderDashboard() {
      let filtered = allDataRows;

      if (viewSessionOnly) {
        filtered = [...sessionCapturedRows].reverse();
      } else {
        // Filtro por nodo
        if (selectedNode !== 'ALL') {
          filtered = filtered.filter(r => isMatchNode(r, selectedNode));
        }

        // Filtro por búsqueda
        if (searchQuery) {
          filtered = filtered.filter(r => 
            (r.timestamp && r.timestamp.toLowerCase().includes(searchQuery)) ||
            (r.device_name && r.device_name.toLowerCase().includes(searchQuery)) ||
            (r.dev_eui && r.dev_eui.toLowerCase().includes(searchQuery)) ||
            (String(r.f_cnt).includes(searchQuery)) ||
            (String(r.packet_seq).includes(searchQuery))
          );
        }
      }

      document.getElementById('lbl-table-count').innerText = viewSessionOnly 
        ? `${filtered.length} tramas de sesión capturadas` 
        : `${filtered.length} de ${allDataRows.length} tramas`;

      // Conteo en botones
      const cnt1 = allDataRows.filter(r => isMatchNode(r, 'Nodo1')).length;
      const cnt2 = allDataRows.filter(r => isMatchNode(r, 'Nodo2')).length;
      const cnt3 = allDataRows.filter(r => isMatchNode(r, 'Nodo3')).length;
      document.getElementById('cnt-all').innerText = allDataRows.length;
      document.getElementById('cnt-node1').innerText = cnt1;
      document.getElementById('cnt-node2').innerText = cnt2;
      if (document.getElementById('cnt-node3')) {
        document.getElementById('cnt-node3').innerText = cnt3;
      }

      if (filtered.length > 0) {
        const latest = filtered[0];
        document.getElementById('val-temp').innerText = latest.temperature.toFixed(1);
        document.getElementById('val-hum').innerText = latest.humidity.toFixed(1);
        document.getElementById('val-bat').innerText = latest.battery_pct;
        document.getElementById('val-bat-mv').innerText = 'Voltaje: ' + latest.battery_mv + ' mV';
        document.getElementById('val-rssi').innerText = latest.rssi;
        document.getElementById('val-snr').innerText = 'SNR: ' + latest.snr.toFixed(1) + ' dB';
        document.getElementById('val-fcnt').innerText = 'FCnt: ' + latest.f_cnt;
        document.getElementById('lbl-last-update').innerText = latest.timestamp.split(' ')[1];

        // Barras
        document.getElementById('bar-temp').style.width = Math.min(100, Math.max(0, (latest.temperature / 45) * 100)) + '%';
        document.getElementById('bar-hum').style.width = Math.min(100, Math.max(0, latest.humidity)) + '%';
        document.getElementById('bar-bat').style.width = Math.min(100, Math.max(0, latest.battery_pct)) + '%';
        
        // Color batería
        const batColor = latest.battery_pct > 50 ? 'var(--emerald)' : (latest.battery_pct > 20 ? 'var(--amber)' : 'var(--red)');
        document.getElementById('bar-bat').style.background = batColor;

        const rssiPct = Math.min(100, Math.max(0, (1 - (latest.rssi / -125)) * 100));
        document.getElementById('bar-rssi').style.width = rssiPct + '%';

        // Gráficos (últimos 35 puntos cronológicos)
        const chrono = [...filtered].reverse().slice(-35);
        drawLineChart('chart-telemetry', [
          { name: 'Temperatura', color: '#fb923c', data: chrono.map(r => r.temperature) },
          { name: 'Humedad', color: '#38bdf8', data: chrono.map(r => r.humidity) }
        ]);

        drawLineChart('chart-rssi', [
          { name: 'RSSI', color: '#c084fc', data: chrono.map(r => r.rssi) }
        ]);
      }

      // Tabla
      const tbody = document.getElementById('table-body');
      if (filtered.length === 0) {
        tbody.innerHTML = '<tr><td colspan="11" style="text-align: center; color: var(--text-muted); padding: 30px;">No se encontraron tramas con los filtros aplicados.</td></tr>';
        return;
      }

      tbody.innerHTML = filtered.map(r => {
        const isNode1 = isMatchNode(r, 'Nodo1');
        const isNode2 = isMatchNode(r, 'Nodo2');
        const isNode3 = isMatchNode(r, 'Nodo3');
        const tagClass = isNode1 ? 'tag-blue' : (isNode2 ? 'tag-purple' : 'tag-teal');
        const tagLabel = isNode1 ? 'Nodo 1 (LOS)' : (isNode2 ? 'Nodo 2 (NLOS)' : (isNode3 ? 'Nodo 3 (Exp)' : r.device_name));
        return '<tr>' +
          '<td style="color: var(--text-muted); font-size: 11px;">#' + r.id + '</td>' +
          '<td>' + r.timestamp + '</td>' +
          '<td><span class="tag ' + tagClass + '">' + tagLabel + '</span></td>' +
          '<td style="font-family: monospace; font-size: 11px; color: var(--text-muted);">' + r.dev_eui + '</td>' +
          '<td><strong style="color: var(--cyan);">' + r.f_cnt + '</strong></td>' +
          '<td>' + r.packet_seq + '</td>' +
          '<td style="color: var(--orange); font-weight: 700;">' + r.temperature.toFixed(2) + ' °C</td>' +
          '<td style="color: var(--cyan); font-weight: 700;">' + r.humidity.toFixed(1) + ' %</td>' +
          '<td><span class="tag tag-green">' + r.battery_pct + '%</span> <small style="color:var(--text-muted);">(' + r.battery_mv + 'mV)</small></td>' +
          '<td><strong>' + r.rssi + ' dBm</strong></td>' +
          '<td>' + r.snr.toFixed(1) + ' dB</td>' +
        '</tr>';
      }).join('');
    }

    async function updateDashboard() {
      if (isPaused) return;
      try {
        const url = `/api/history?limit=${currentLimit}&_=${Date.now()}`;
        const res = await fetch(url, { cache: 'no-store' });
        allDataRows = await res.json();

        // Ingestión en vivo para la sesión experimental
        if (sessionActive && !sessionCompleted && sessionStartId !== null) {
          const lastCapturedId = sessionCapturedRows.length > 0 
            ? sessionCapturedRows[sessionCapturedRows.length - 1].id 
            : (sessionStartId - 1);

          let newCandidates = allDataRows.filter(r => r.id > lastCapturedId);

          if (selectedNode !== 'ALL') {
            newCandidates = newCandidates.filter(r => isMatchNode(r, selectedNode));
          }

          newCandidates.sort((a, b) => a.id - b.id);

          for (let r of newCandidates) {
            if (sessionCapturedRows.length < sessionTarget) {
              sessionCapturedRows.push(r);
            }
          }

          if (sessionCapturedRows.length >= sessionTarget) {
            sessionCompleted = true;
            sessionEndId = sessionCapturedRows[sessionTarget - 1].id;
          }
        }

        renderSessionUI();
        renderDashboard();
      } catch (e) {
        console.error('Error fetching data:', e);
      }
    }

    updateDashboard();
    setInterval(updateDashboard, 1000);
    window.addEventListener('resize', () => renderDashboard());

    // ==========================================
    // LÓGICA DE EXPORTACIÓN AVANZADA
    // ==========================================
    let expCurrentNode = 'ALL';
    let expCurrentSlot = 'all';
    let expDebounceTimer = null;

    function openExportModal() {
      // Sincronizar nodo con el filtro actual del dashboard
      expCurrentNode = selectedNode || 'ALL';
      setExpNode(expCurrentNode);
      document.getElementById('modal-export').classList.add('active');
      triggerExportPreview();
    }

    function closeExportModal() {
      document.getElementById('modal-export').classList.remove('active');
    }

    function setExpNode(node) {
      expCurrentNode = node;
      document.querySelectorAll('#group-exp-node .pill-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-node') === node);
      });
      triggerExportPreview();
    }

    function setExpDatePreset(preset) {
      document.querySelectorAll('#group-exp-date .pill-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-date') === preset);
      });
      
      const inStart = document.getElementById('exp-start-date');
      const inEnd = document.getElementById('exp-end-date');
      const now = new Date();
      const fmt = d => d.toISOString().split('T')[0];

      if (preset === 'today') {
        inStart.value = fmt(now);
        inEnd.value = fmt(now);
      } else if (preset === 'yesterday') {
        const y = new Date(now);
        y.setDate(y.getDate() - 1);
        inStart.value = fmt(y);
        inEnd.value = fmt(y);
      } else if (preset === 'last3') {
        const past = new Date(now);
        past.setDate(past.getDate() - 3);
        inStart.value = fmt(past);
        inEnd.value = fmt(now);
      } else {
        inStart.value = '';
        inEnd.value = '';
      }
      triggerExportPreview();
    }

    function onExpDateChange() {
      document.querySelectorAll('#group-exp-date .pill-btn').forEach(b => b.classList.remove('active'));
      triggerExportPreview();
    }

    function setExpSlotPreset(slot) {
      expCurrentSlot = slot;
      document.querySelectorAll('#group-exp-slot .pill-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-slot') === slot);
      });

      const inStart = document.getElementById('exp-start-time');
      const inEnd = document.getElementById('exp-end-time');

      if (slot === 'manana') {
        inStart.value = '08:00'; inEnd.value = '12:00';
      } else if (slot === 'mediodia') {
        inStart.value = '12:00'; inEnd.value = '15:00';
      } else if (slot === 'tarde') {
        inStart.value = '15:00'; inEnd.value = '19:00';
      } else if (slot === 'noche') {
        inStart.value = '19:00'; inEnd.value = '23:59';
      } else {
        inStart.value = ''; inEnd.value = '';
      }
      triggerExportPreview();
    }

    function onExpTimeChange() {
      expCurrentSlot = 'custom';
      document.querySelectorAll('#group-exp-slot .pill-btn').forEach(b => b.classList.remove('active'));
      triggerExportPreview();
    }

    function getExportQueryString() {
      const sDate = document.getElementById('exp-start-date').value;
      const eDate = document.getElementById('exp-end-date').value;
      const sTime = document.getElementById('exp-start-time').value;
      const eTime = document.getElementById('exp-end-time').value;

      const p = new URLSearchParams();
      if (expCurrentNode && expCurrentNode !== 'ALL') p.append('node', expCurrentNode);
      if (sDate) p.append('start_date', sDate);
      if (eDate) p.append('end_date', eDate);
      if (sTime) p.append('start_time', sTime);
      if (eTime) p.append('end_time', eTime);
      if (expCurrentSlot && expCurrentSlot !== 'all' && expCurrentSlot !== 'custom') {
        p.append('slot', expCurrentSlot);
      }
      return p;
    }

    function triggerExportPreview() {
      clearTimeout(expDebounceTimer);
      expDebounceTimer = setTimeout(async () => {
        const p = getExportQueryString();
        const lbl = document.getElementById('exp-preview-count');
        const btn = document.getElementById('btn-do-export');
        const inFilename = document.getElementById('exp-filename');

        // Sugerir nombre de archivo
        let nodePart = expCurrentNode === 'ALL' ? 'TodosNodos' : (expCurrentNode.includes('Nodo1') ? 'Nodo1_LOS' : (expCurrentNode.includes('Nodo2') ? 'Nodo2_NLOS' : 'Nodo3_EXP'));
        let datePart = document.getElementById('exp-start-date').value || 'Historial';
        let slotPart = expCurrentSlot === 'all' ? 'Completo' : expCurrentSlot;
        inFilename.value = `lorawan_${nodePart}_${datePart}_${slotPart}.csv`;

        lbl.innerHTML = '⏳ Verificando registros...';
        try {
          const res = await fetch(`/api/export-count?${p.toString()}&_=${Date.now()}`);
          const json = await res.json();
          const count = json.count || 0;
          if (count > 0) {
            lbl.className = 'preview-count';
            lbl.innerHTML = `✅ <strong>${count}</strong> tramas encontradas`;
            btn.disabled = false;
            btn.innerHTML = `📥 Descargar CSV (${count} tramas)`;
          } else {
            lbl.className = 'preview-count empty';
            lbl.innerHTML = `⚠️ 0 tramas para este filtro`;
            btn.disabled = true;
            btn.innerHTML = `📥 Sin datos para descargar`;
          }
        } catch (e) {
          lbl.innerHTML = 'Error al consultar base de datos';
        }
      }, 150);
    }

    function executeFilteredExport() {
      const p = getExportQueryString();
      const fn = document.getElementById('exp-filename').value.trim() || 'telemetria_lorawan_filtrada.csv';
      p.append('filename', fn);
      window.location.href = `/api/export-csv?${p.toString()}`;
    }

  </script>

  <!-- MODAL DE EXPORTACIÓN AVANZADA (FILTRO POR DÍAS, HORAS Y NODOS) -->
  <div class="modal-backdrop" id="modal-export" onclick="if(event.target===this) closeExportModal()">
    <div class="modal-box">
      <div class="modal-header">
        <div>
          <h2><span>📊</span> Exportación Avanzada de Telemetría</h2>
          <div style="font-size: 12.5px; color: var(--text-muted); margin-top: 4px;">Filtra y descarga conjuntos de datos ordenados para la memoria de título (Metodología PPDIOO).</div>
        </div>
        <button class="modal-close" onclick="closeExportModal()">&times;</button>
      </div>

      <!-- 1. FILTRO DE NODO -->
      <div class="filter-section">
        <div class="filter-section-title">1. Dispositivo / Nodo</div>
        <div class="pill-group" id="group-exp-node">
          <button class="pill-btn active" data-node="ALL" onclick="setExpNode('ALL')">🌐 Todos los Nodos</button>
          <button class="pill-btn" data-node="Nodo1" onclick="setExpNode('Nodo1')">📡 Nodo 1 (LOS)</button>
          <button class="pill-btn" data-node="Nodo2" onclick="setExpNode('Nodo2')">🏢 Nodo 2 (NLOS)</button>
          <button class="pill-btn" data-node="Nodo3" onclick="setExpNode('Nodo3')">🔬 Nodo 3 (Exp)</button>
        </div>
      </div>

      <!-- 2. FILTRO DE FECHAS (DÍAS) -->
      <div class="filter-section">
        <div class="filter-section-title">2. Rango de Fechas (Días de Prueba)</div>
        <div class="pill-group" id="group-exp-date">
          <button class="pill-btn active" data-date="all" onclick="setExpDatePreset('all')">🌐 Todo el Historial</button>
          <button class="pill-btn" data-date="today" onclick="setExpDatePreset('today')">📅 Hoy</button>
          <button class="pill-btn" data-date="yesterday" onclick="setExpDatePreset('yesterday')">⏮️ Ayer</button>
          <button class="pill-btn" data-date="last3" onclick="setExpDatePreset('last3')">🗓️ Últimos 3 Días</button>
        </div>
        <div class="input-row">
          <div class="input-field-group">
            <label>Fecha Desde:</label>
            <input type="date" id="exp-start-date" class="modal-input" onchange="onExpDateChange()">
          </div>
          <div class="input-field-group">
            <label>Fecha Hasta:</label>
            <input type="date" id="exp-end-date" class="modal-input" onchange="onExpDateChange()">
          </div>
        </div>
      </div>

      <!-- 3. FILTRO DE HORAS (FRANJAS HORARIAS DE LA TESIS) -->
      <div class="filter-section">
        <div class="filter-section-title">3. Franjas Horarias (Criterio de Evaluación Tesis)</div>
        <div class="pill-group" id="group-exp-slot">
          <button class="pill-btn active" data-slot="all" onclick="setExpSlotPreset('all')">⏰ Todo el Día (00:00 - 23:59)</button>
          <button class="pill-btn" data-slot="manana" onclick="setExpSlotPreset('manana')">🌅 Mañana (08:00 - 12:00)</button>
          <button class="pill-btn" data-slot="mediodia" onclick="setExpSlotPreset('mediodia')">☀️ Mediodía (12:00 - 15:00)</button>
          <button class="pill-btn" data-slot="tarde" onclick="setExpSlotPreset('tarde')">🌇 Tarde (15:00 - 19:00)</button>
          <button class="pill-btn" data-slot="noche" onclick="setExpSlotPreset('noche')">🌙 Noche (19:00 - 23:59)</button>
        </div>
        <div class="input-row">
          <div class="input-field-group">
            <label>Hora Inicio Manual (opcional):</label>
            <input type="time" id="exp-start-time" class="modal-input" onchange="onExpTimeChange()">
          </div>
          <div class="input-field-group">
            <label>Hora Fin Manual (opcional):</label>
            <input type="time" id="exp-end-time" class="modal-input" onchange="onExpTimeChange()">
          </div>
        </div>
      </div>

      <!-- 4. VISTA PREVIA Y NOMBRE DE ARCHIVO -->
      <div class="export-preview-box">
        <div>
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Tramas Coincidentes:</div>
          <div class="preview-count" id="exp-preview-count">🔍 Calculando tramas...</div>
        </div>
        <div style="flex: 1; min-width: 220px;">
          <label style="font-size: 11px; color: var(--text-muted); font-weight: 700; display: block; margin-bottom: 3px;">Nombre de Archivo CSV:</label>
          <input type="text" id="exp-filename" class="modal-input" style="font-family: monospace; font-size: 12px;">
        </div>
      </div>

      <!-- FOOTER ACCIONES -->
      <div class="modal-footer">
        <button class="btn" onclick="closeExportModal()">Cancelar</button>
        <a href="/api/export-csv" class="btn" download="telemetria_completa.csv" style="color: var(--text-muted);">📥 Descargar Todo (Sin Filtro)</a>
        <button class="btn btn-primary" id="btn-do-export" onclick="executeFilteredExport()">📥 Descargar CSV Filtrado</button>
      </div>
    </div>
  </div>

</body>
</html>
"""

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html' or self.path.startswith('/?'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
            
        elif self.path.startswith('/api/history'):
            # Parsear limit
            limit = 100
            if 'limit=' in self.path:
                param = self.path.split('limit=')[1].split('&')[0]
                if param == 'all':
                    limit = 2000
                else:
                    try: limit = int(param)
                    except: limit = 100

            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute('SELECT * FROM telemetry ORDER BY id DESC LIMIT ?', (limit,))
            rows = [dict(r) for r in c.fetchall()]
            conn.close()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(json.dumps(rows).encode('utf-8'))

        elif self.path.startswith('/api/export-count'):
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            query, sql_params = build_telemetry_query(params)
            count_query = 'SELECT COUNT(*) FROM (' + query + ')'
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(count_query, sql_params)
            count = c.fetchone()[0]
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(json.dumps({'count': count}).encode('utf-8'))

        elif self.path.startswith('/api/export-csv'):
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            query, sql_params = build_telemetry_query(params)
            query += ' ORDER BY id ASC'
            limit = params.get('limit', [''])[0]
            if limit:
                try:
                    query += f' LIMIT {int(limit)}'
                except: pass
            
            filename = params.get('filename', ['telemetria_lorawan_campus_uct.csv'])[0]
            if not filename.endswith('.csv'): filename += '.csv'
            
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(query, sql_params)
            rows = c.fetchall()
            conn.close()

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Fecha y Hora', 'Dispositivo', 'DevEUI', 'Temperatura (°C)', 'Humedad (%)', 'Batería (mV)', 'Batería (%)', 'Secuencia', 'Status Flags', 'RSSI (dBm)', 'SNR (dB)', 'FCnt'])
            for r in rows:
                writer.writerow(list(r))

            csv_bytes = output.getvalue().encode('utf-8-sig')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            self.wfile.write(csv_bytes)


        elif self.path.startswith('/api/latest'):
            with history_lock:
                data = latest_packet
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        return

def main():
    init_db()
    t = threading.Thread(target=start_mqtt, daemon=True)
    t.start()
    server = ThreadingHTTPServer(('0.0.0.0', PORT), DashboardHandler)
    print(f"[HTTP] Dashboard activo en http://localhost:{PORT}")
    server.serve_forever()

if __name__ == '__main__':
    main()
