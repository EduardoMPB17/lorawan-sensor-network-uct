# Herramientas CLI y Automatización - Red LoRaWAN UCT

Este directorio contiene herramientas de línea de comandos (CLI) y puentes de red utilizados durante las pruebas de campo y la monitorización de telemetría.

---

## 1. Catálogo de Scripts

### `monitor_lorawan.py`
Monitor de consola en tiempo real para visualizar tramas LoRaWAN entrantes desde el broker MQTT local.
* **Uso:**
  ```bash
  python monitor_lorawan.py
  ```
* **Métricas visualizadas:** Dispositivo de origen, DevEUI, contador de tramas (`fCnt`), temperatura (°C), humedad relativa (%), nivel de batería (mV y %), RSSI (dBm) y relación señal a ruido (SNR en dB).

### `bridge_cloud.py`
Puente MQTT unidireccional que captura los eventos publicados por el gateway en el broker local (`192.168.200.45:1883`) y los retransmite hacia un broker público en la nube (ej. EMQX en `broker.emqx.io`).
* **Tópico publicado:** `uct/campus-rivas/telemetria/up`
* **Uso:**
  ```bash
  python bridge_cloud.py
  ```
* **Utilidad:** Permite la visualización remota de telemetría en dispositivos fuera de la red local del campus durante campañas de pruebas exteriores.

---

## 2. Requisitos de Ejecución

* Python 3.8+
* Librería `paho-mqtt`:
  ```bash
  pip install paho-mqtt
  ```
