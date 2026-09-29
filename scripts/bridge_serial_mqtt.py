#!/usr/bin/env python3
"""
=============================================================================
TRABAJO DE TÍTULO - RED LORAWAN CAMPUS DR. LUIS RIVAS DEL CANTO (UCT)
Script Puente: Serial USB (Heltec V3 Receptor) -> MQTT Broker / Ingesta
=============================================================================
Este script escucha la salida JSON del nodo receptor conectado por USB
y reenvía las tramas hacia el Broker MQTT institucional o local con el formato
esperado por el backend y el dashboard web.
"""

import sys
import json
import time
import argparse

try:
    import serial
except ImportError:
    print("[ERROR] Módulo 'pyserial' no instalado. Instalar con: pip install pyserial")
    sys.exit(1)

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("[WARN] Módulo 'paho-mqtt' no instalado. Solo se mostrará por consola.")
    mqtt = None


def main():
    parser = argparse.ArgumentParser(description="Puente Serial LoRa Receptor -> MQTT")
    parser.add_argument("--port", "-p", required=True, help="Puerto COM del Heltec receptor (ej: COM3, COM4, /dev/ttyUSB0)")
    parser.add_argument("--baud", "-b", type=int, default=115200, help="Velocidad en baudios (default: 115200)")
    parser.add_argument("--mqtt-host", default="localhost", help="Host del broker MQTT (default: localhost)")
    parser.add_argument("--mqtt-port", type=int, default=1883, help="Puerto del broker MQTT (default: 1883)")
    parser.add_argument("--mqtt-topic", default="uct/campus/lora/uplink", help="Tópico MQTT de publicación")

    args = parser.parse_args()

    client = None
    if mqtt:
        try:
            client = mqtt.Client()
            client.connect(args.mqtt_host, args.mqtt_port, 60)
            client.loop_start()
            print(f"[MQTT] Conectado exitosamente a {args.mqtt_host}:{args.mqtt_port}")
        except Exception as e:
            print(f"[WARN] No se pudo conectar al broker MQTT ({e}). Modo solo consola activo.")
            client = None

    try:
        ser = serial.Serial(args.port, args.baud, timeout=1)
        print(f"[SERIAL] Abierto puerto {args.port} a {args.baud} baudios.")
        print("[ESCUCHA] Esperando datos del nodo receptor Heltec V3...\n")
    except Exception as e:
        print(f"[ERROR] Error al abrir el puerto serial {args.port}: {e}")
        sys.exit(1)

    try:
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if not line:
                continue

            # Detectar líneas de JSON válidas emitidas por receptor-p2p.ino
            if line.startswith("{") and line.endswith("}"):
                try:
                    payload_json = json.loads(line)
                    # Añadir timestamp ISO 8601 del sistema de recepción
                    payload_json["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

                    print(f"[RX INGESTA] Trama recibida -> Nodo {payload_json.get('node_id')}, "
                          f"Seq: {payload_json.get('sequence')}, "
                          f"Temp: {payload_json.get('temperature')}°C, "
                          f"Hum: {payload_json.get('humidity')}%, "
                          f"RSSI: {payload_json.get('rssi')} dBm")

                    if client:
                        node_topic = f"{args.mqtt_topic}/node_{payload_json.get('node_id')}"
                        client.publish(node_topic, json.dumps(payload_json))
                        print(f"  -> Publicado en MQTT: {node_topic}")

                except json.JSONDecodeError:
                    pass
            else:
                # Mostrar logs de depuración del firmware
                print(f"[RADIO] {line}")

    except KeyboardInterrupt:
        print("\n[INFO] Cerrando puente serial.")
    finally:
        ser.close()
        if client:
            client.loop_stop()
            client.disconnect()


if __name__ == "__main__":
    main()
