# Scripts de Utilidad y Automatización LoRaWAN

Este directorio contiene herramientas de línea de comandos (CLI), puentes de comunicación y scripts auxiliares utilizados para pruebas, monitoreo y exportación de telemetría.

---

## 1. Descripción de Scripts

### `monitor_lorawan.py`
Monitor de consola en tiempo real para visualizar las tramas LoRaWAN recibidas vía MQTT.
* **Uso:**
  ```bash
  python monitor_lorawan.py
  ```
* **Salida:** Muestra en pantalla el dispositivo, DevEUI, temperatura (°C), humedad (%), nivel de batería, RSSI (dBm), SNR (dB) y secuencia de tramas.

### `bridge_cloud.py`
Puente bidireccional/unidireccional MQTT que reenvía los eventos de telemetría capturados en el broker local Mosquitto (`192.168.200.45:1883`) hacia un broker en la nube (ej. EMQX público en `broker.emqx.io`).
* **Tópico publicado:** `uct/campus-rivas/telemetria/up`
* **Uso:**
  ```bash
  python bridge_cloud.py
  ```
* Permite visualizar las tramas de manera remota fuera de la intranet de la UCT durante pruebas de campo.

### `bridge_serial_mqtt.py`
Script legado para captura y reenvío de datos vía puerto serie (UART) hacia un broker MQTT local cuando se prueban nodos conectados directamente por USB.

### `crear_configs_chirpstack.py`
Generador automatizado de plantillas de configuración y perfiles de dispositivos para despliegues con ChirpStack v4.

### `update_dashboard_filters.py`
Script de mantenimiento y actualización de filtros para sincronizar el soporte del Nodo 3 (`Heltec-V3-Nodo3B`) en interfaces históricas de visualización.

