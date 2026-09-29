# Banco de Pruebas de Radio P2P (Sin Gateway)

Este entorno permite realizar pruebas de enlace físico y transmisión de telemetría de radiofrecuencia (915 MHz) utilizando **dos placas Heltec WiFi LoRa 32 V3** sin requerir un Gateway concentrador ni la instancia de ChirpStack.

---

## Estructura de este directorio
```text
firmware/prueba-nodos/
├── emisor-p2p/
│   ├── emisor-p2p.ino    # Firmware para la placa Heltec #1 (Transmisor)
│   ├── config.h          # Configuración de radio (916.8 MHz, SF7, 14 dBm)
│   └── payload.h         # Codificación binaria de 10 bytes (idéntica a LoRaWAN)
└── receptor-p2p/
    ├── receptor-p2p.ino  # Firmware para la placa Heltec #2 (Receptor / Bridge)
    └── config.h          # Parámetros de radio coincidentes
```

---

## 1. Conexión de Antenas (Regla Obligatoria RT2)
**ATENCIÓN:** Conecta obligatoriamente la antena de 915 MHz a ambas placas Heltec V3 **antes** de conectarlas al puerto USB.

---

## 2. Instrucciones para la Placa #1 (Emisor)
1. Conecta la primera placa Heltec V3 a tu PC.
2. Abre en Arduino IDE el archivo [`emisor-p2p.ino`](file:///c:/Users/Administrador/Desktop/Tesis/lorawan-sensor-network-uct/firmware/prueba-nodos/emisor-p2p/emisor-p2p.ino).
3. Selecciona la placa **Heltec WiFi LoRa 32(V3)** y el puerto COM asignado.
4. Carga el código.
5. Puedes alimentarla mediante USB, un powerbank o una batería LiPo para moverla por distintas zonas del campus o de tu casa.

---

## 3. Instrucciones para la Placa #2 (Receptor / Gateway Virtual)
1. Conecta la segunda placa Heltec V3 a tu PC.
2. Abre en Arduino IDE el archivo [`receptor-p2p.ino`](file:///c:/Users/Administrador/Desktop/Tesis/lorawan-sensor-network-uct/firmware/prueba-nodos/receptor-p2p/receptor-p2p.ino).
3. Selecciona el puerto COM de esta segunda placa y carga el código.
4. Abre el Monitor Serial a **115200 baud**.
5. Verás inmediatamente:
   * La llegada de las tramas de 10 bytes.
   * La decodificación de `Temperatura`, `Humedad` y `Batería`.
   * Las métricas de canal en tiempo real: **RSSI** (dBm) y **SNR** (dB).
   * La línea de salida en formato JSON lista para alimentar el script puente o el dashboard.

---

## 4. Reenvío a MQTT (Opcional)
Para alimentar el backend y dashboard desde la placa receptora:
```bash
python scripts/bridge_serial_mqtt.py --port COM_DE_TU_RECEPTOR
```
