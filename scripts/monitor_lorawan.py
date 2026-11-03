# -*- coding: utf-8 -*-
"""
Monitor en tiempo real de telemetría LoRaWAN desde Gateway Milesight UG63
Proyecto de Título - Universidad Católica de Temuco (UCT)
"""
import base64
import json
import paho.mqtt.client as mqtt

BROKER = "127.0.0.1"
PORT = 1883
TOPIC = "#"  # Escucha todos los eventos del gateway

def decodificar_10_bytes(raw_bytes):
    if len(raw_bytes) < 10:
        return None
    
    nodo_id = raw_bytes[0]
    secuencia = int.from_bytes(raw_bytes[1:5], byteorder="big", signed=False)
    temp_raw = int.from_bytes(raw_bytes[5:7], byteorder="big", signed=True)
    temperatura = round(temp_raw / 100.0, 2)
    hum_raw = int.from_bytes(raw_bytes[7:9], byteorder="big", signed=False)
    humedad = round(hum_raw / 100.0, 1)
    bat_raw = raw_bytes[9]
    bateria = round((bat_raw / 100.0) + 2.0, 2)

    return {
        "nodo_id": nodo_id,
        "secuencia": secuencia,
        "temperatura": temperatura,
        "humedad": humedad,
        "bateria": bateria
    }

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("\n========================================================")
        print("  CONECTADO AL BROKER MQTT LOCAL (DOCKER) EXITOSAMENTE   ")
        print("  Esperando transmisiones del Gateway Milesight UG63... ")
        print("========================================================\n")
        client.subscribe(TOPIC)
    else:
        print(f"Error al conectar con broker, código: {rc}")

def on_message(client, userdata, msg):
    print("\n--------------------------------------------------------")
    print(f"[NUEVO PAQUETE MQTT] Tópico: {msg.topic}")
    
    try:
        payload_str = msg.payload.decode("utf-8")
        data_json = json.loads(payload_str)
        print(f"JSON Crudo recibido:")
        print(json.dumps(data_json, indent=2))
        
        # Buscar campo de payload (data en base64 o data_hex)
        raw_bytes = None
        if "data" in data_json:
            try:
                raw_bytes = base64.b64decode(data_json["data"])
            except Exception:
                pass
        elif "data_hex" in data_json:
            raw_bytes = bytes.fromhex(data_json["data_hex"])
        
        if raw_bytes:
            print(f"\nPayload Bytes (HEX): {raw_bytes.hex().upper()}")
            telemetria = decodificar_10_bytes(raw_bytes)
            if telemetria:
                print("\n>>> DATOS DEL SENSOR HELTEC V3 DECODIFICADOS <<<")
                print(f"  * ID del Nodo:     {telemetria['nodo_id']}")
                print(f"  * Paquete N°:      #{telemetria['secuencia']}")
                print(f"  * Temperatura:     {telemetria['temperatura']} °C")
                print(f"  * Humedad:         {telemetria['humedad']} %")
                print(f"  * Tensión Batería: {telemetria['bateria']} V")
        
        # Métricas RF si vienen en el JSON
        rssi = data_json.get("rssi")
        snr = data_json.get("snr") or data_json.get("loRaSNR")
        if rssi is not None:
            print(f"  * Nivel RSSI:      {rssi} dBm")
        if snr is not None:
            print(f"  * Relación SNR:    {snr} dB")

    except Exception as e:
        print(f"Mensaje en texto plano: {msg.payload}")
    print("--------------------------------------------------------")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(BROKER, PORT, 60)
    client.loop_forever()
except KeyboardInterrupt:
    print("\nMonitor detenido por el usuario.")
except Exception as e:
    print(f"Error conectando al broker local: {e}")
