"""
Bridge de Retransmisión LoRaWAN: Local -> Broker Cloud (Internet)
Trabajo de Título INFO-1197 - Universidad Católica de Temuco
Autor: Eduardo Mariqueo

Este script se suscribe a los eventos del servidor local (Milesight UG65 / Mosquitto)
y retransmite automáticamente cada trama hacia un broker MQTT público en Internet,
permitiendo que cualquier persona o dashboard externo consuma la telemetría en tiempo real.
"""

import json
import time
import paho.mqtt.client as mqtt

# -------------------------------------------------------------
# 1. CONFIGURACIÓN LOCAL (Tu laptop / Gateway UG65)
# -------------------------------------------------------------
LOCAL_BROKER = "127.0.0.1"
LOCAL_PORT = 1883
LOCAL_TOPIC = "application/sensores-campus/device/+/event/up"

# -------------------------------------------------------------
# 2. CONFIGURACIÓN CLOUD (Internet público)
# -------------------------------------------------------------
CLOUD_BROKER = "broker.emqx.io"
CLOUD_PORT = 1883
CLOUD_TOPIC = "uct/campus-rivas/telemetria/up"

# Clientes MQTT
client_local = mqtt.Client(client_id="bridge_local_sub")
client_cloud = mqtt.Client(client_id=f"bridge_uct_cloud_{int(time.time())}")

def on_cloud_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[CLOUD] Conectado exitosamente al broker de Internet: {CLOUD_BROKER}:{CLOUD_PORT}", flush=True)
    else:
        print(f"[CLOUD Error] No se pudo conectar al broker de Internet (rc={rc})", flush=True)

def on_local_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"[LOCAL] Conectado a Mosquitto local en {LOCAL_BROKER}:{LOCAL_PORT}", flush=True)
        client.subscribe(LOCAL_TOPIC)
        print(f"[LOCAL] Suscrito al tópico: {LOCAL_TOPIC}", flush=True)
    else:
        print(f"[LOCAL Error] Error de conexión local (rc={rc})", flush=True)

def on_local_message(client, userdata, msg):
    try:
        topic = msg.topic
        payload_raw = msg.payload.decode('utf-8', errors='ignore')
        data = json.loads(payload_raw)

        print(f"\n[EVENTO RECIBIDO] Tópico: {topic}", flush=True)
        print(f"-> Datos: {data}", flush=True)

        # Retransmitir al broker de Internet
        client_cloud.publish(CLOUD_TOPIC, json.dumps(data), qos=0)
        print(f"[RETRANSMISIÓN OK] -> Enviado a Internet: {CLOUD_TOPIC}", flush=True)

    except Exception as e:
        print(f"[ERROR Procesando Trama]: {e}", flush=True)

def main():
    print("=" * 65, flush=True)
    print("  Iniciando Bridge LoRaWAN UCT: Gateway UG65 -> Internet", flush=True)
    print(f"  Destino público: {CLOUD_BROKER} -> Tópico: {CLOUD_TOPIC}", flush=True)
    print("=" * 65, flush=True)

    client_cloud.on_connect = on_cloud_connect
    client_local.on_connect = on_local_connect
    client_local.on_message = on_local_message

    try:
        print(f"[1/2] Conectando a broker de Internet ({CLOUD_BROKER})...", flush=True)
        client_cloud.connect(CLOUD_BROKER, CLOUD_PORT, 60)
        client_cloud.loop_start()

        print(f"[2/2] Conectando a broker local ({LOCAL_BROKER})...", flush=True)
        client_local.connect(LOCAL_BROKER, LOCAL_PORT, 60)
        client_local.loop_forever()

    except KeyboardInterrupt:
        print("\nDeteniendo bridge...", flush=True)
        client_local.disconnect()
        client_cloud.disconnect()
    except Exception as e:
        print(f"[FATAL ERROR] {e}", flush=True)

if __name__ == '__main__':
    main()
