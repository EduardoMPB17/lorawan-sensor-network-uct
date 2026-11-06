# Firmware Oficial de Nodos Sensores - Red LoRaWAN Campus UCT

Este directorio contiene el código fuente en C/C++ para los nodos sensores Heltec WiFi LoRa 32 V3 desplegados en el **Campus Dr. Luis Rivas del Canto**, Universidad Católica de Temuco.

El esquema experimental está compuesto por **4 programas oficiales** distribuidos en dos tipos de sesiones de prueba para evaluar los objetivos de calidad de servicio (QoS) de la tesis:

```text
firmware/
├── sesion-tipo-a/                       # Tramas no confirmadas para medir Packet Loss (PL <= 10%)
│   ├── nodo1_heltec_v3_tipoA/           # Nodo 1 - LOS (Línea de Vista)
│   │   └── nodo1_heltec_v3_tipoA.ino
│   └── nodo2_heltec_v3_tipoA/           # Nodo 2 - NLOS (Obstruido / Shadowing)
│       └── nodo2_heltec_v3_tipoA.ino
└── sesion-tipo-b/                       # Tramas confirmadas para medir Retardo T_conf (<= 6.0 s)
    ├── nodo1_heltec_v3_tipoB/           # Nodo 1 - LOS (Línea de Vista)
    │   └── nodo1_heltec_v3_tipoB.ino
    └── nodo2_heltec_v3_tipoB/           # Nodo 2 - NLOS (Obstruido / Shadowing)
        └── nodo2_heltec_v3_tipoB.ino
```

---

## 1. Especificaciones de Hardware

* **Módulo Base:** Heltec WiFi LoRa 32 V3 (SoC Espressif ESP32-S3FN8 dual-core + transceptor Semtech SX1262).
* **Sensor de Telemetría:** DHT11 (temperatura ambiente y humedad relativa).
* **Pantalla de Diagnóstico:** OLED 0.96" monocromática SSD1306 (I2C integrado).

### Mapeo de Pines (ESP32-S3)
| Componente | Línea | Pin GPIO | Descripción |
|---|---|---|---|
| **DHT11** | DATA | **GPIO 4** | Señal de datos del sensor (alimentación 3V3 y GND) |
| **OLED** | SDA | **GPIO 17** | Bus de datos I2C |
| **OLED** | SCL | **GPIO 18** | Bus de reloj I2C |
| **OLED / Periféricos** | RST | **GPIO 21** | Reset de pantalla |
| **Alimentación Vext** | Vext Control | **GPIO 36** | **Activo en LOW** (energiza el riel de periféricos y SX1262) |
| **LED Usuario** | Ánodo | **GPIO 35** | Indicador lumínico de transmisión / estado |
| **SX1262** | NSS / CS | **GPIO 8** | Selección de chip SPI |
| **SX1262** | RST | **GPIO 12** | Reset del transceptor LoRa |
| **SX1262** | BUSY | **GPIO 13** | Indicador de radio ocupada |
| **SX1262** | DIO1 | **GPIO 14** | Interrupción IRQ (TxDone / RxTimeout / RxDone) |

> [!CAUTION]
> **Regla de Hardware RT2:** **OBLIGATORIO** conectar la antena omnidireccional de 915 MHz antes de energizar la placa. Energizar el chip SX1262 sin antena genera ondas estacionarias de alta reflectancia que dañan de forma irreversible el amplificador de potencia (PA) de RF.

---

## 2. Parámetros LoRaWAN y Plan Regional

* **Banda Regional:** AU915, **Sub-banda 2** (Canales 8 al 15: frecuencias de subida 916.8 MHz a 918.2 MHz).
* **Ventana RX2 Downlink:** Frecuencia 923.3 MHz, DR8 (SF12 / 500 kHz).
* **Potencia de Emisión:** **14 dBm (25 mW)** (conforme a Resoluciones Exentas N.º 1.985/2017 y N.º 737/2025 de SUBTEL).
* **Datarate Uplink:** DR5 (SF7 / BW 125 kHz) $\rightarrow$ Time on Air (ToA) $\approx 46.3\text{ ms}$.

---

## 3. Credenciales OTAA y Asignación de Nodos

* **JoinEUI (AppEUI):** `0000000000000000`
* **AppKey (común):** `2B 7E 15 16 28 AE D2 A6 AB F7 15 88 09 CF 4F 3C`

| Sketch | Rol Experimental | DevEUI | Primer Byte Payload (`node_id`) | Nombre en NS UG65 |
|---|---|---|---|---|
| `nodo1_heltec_v3_tipoA.ino` | Sesión Tipo A - LOS (Edif. 16 Ing. en Construcción) | `0102030405060708` | `0x01` | `Heltec-V3-Nodo1` |
| `nodo2_heltec_v3_tipoA.ino` | Sesión Tipo A - NLOS (Edif. 08 Dirección de Informática) | `0102030405060709` | `0x02` | `Heltec-V3-Nodo2` |
| `nodo1_heltec_v3_tipoB.ino` | Sesión Tipo B - LOS (Edif. 16 Ing. en Construcción) | `0102030405060708` | `0x01` | `Heltec-V3-Nodo1` |
| `nodo2_heltec_v3_tipoB.ino` | Sesión Tipo B - NLOS (Edif. 08 Dirección de Informática) | `0102030405060709` | `0x02` | `Heltec-V3-Nodo2` |

---

## 4. Estructura de Payload Binario (10 Bytes Big-Endian)

Los 4 códigos empaquetan la telemetría en un buffer estricto de 10 bytes:
```
+------------+----------------------+--------------------+-------------------+---------------------+
| Byte 0     | Bytes 1-4            | Bytes 5-6          | Bytes 7-8         | Byte 9              |
| Node ID    | Sequence (FCnt)      | Temp * 100         | Hum * 100         | (Vbat - 2.0) * 100  |
| uint8_t    | uint32_t (MSB first) | int16_t (MSB first)| uint16_t (MSB)    | uint8_t             |
+------------+----------------------+--------------------+-------------------+---------------------+
```

---

## 5. Descripción de Sesiones Experimentales

### Sesión Tipo A (Evaluación de Packet Loss - RQS1: $PL \le 10\,\%$)
* **Modo MAC:** Tramas no confirmadas (`unconfirmed uplink`, `NbTrans = 1`).
* **Objetivo:** Transmitir 100 tramas sin reintentos automáticos que enmascaren pérdidas de canal.
* **Métrica:** Se calcula la tasa de paquetes perdidos mediante huecos en la secuencia recibida en el dashboard:
  $$PL = \left(1 - \frac{\text{Tramas Recibidas}}{100}\right) \times 100\,\%$$

### Sesión Tipo B (Evaluación de Retardo de Confirmación - RQS2: $T_{\text{conf}} \le 6.0\text{ s}$)
* **Modo MAC:** Tramas confirmadas (`confirmed uplink`).
* **Objetivo:** Medir el tiempo de ida y vuelta (round-trip) hasta la recepción del ACK en ventana RX1 (1 s) o RX2 (2 s):
  $$T_{\text{conf}} = T_{\text{ACK}} - T_{\text{env}}$$
* **Medición:** El firmware registra la marca temporal con `millis()` antes de transmitir y al recibir el ACK, mostrándola en la pantalla OLED y puerto serie. La sesión se detiene automáticamente en el dashboard al completar $\ge 30$ tramas.

---

## 6. Instrucciones de Compilación y Flasheo (Arduino IDE)

1. **Instalar el soporte ESP32 en Arduino IDE:**
   - Preferencias $\rightarrow$ Gestor de URLs Adicionales de Tarjetas:
     `https://espressif.github.io/arduino-esp32/package_esp32_index.json`
   - Instalar `esp32` por Espressif Systems en el Gestor de Tarjetas.
2. **Instalar librerías requeridas:**
   - `RadioLib` (v6.0+)
   - `Adafruit SSD1306`
   - `Adafruit GFX Library`
   - `Adafruit DHT sensor library`
3. **Seleccionar tarjeta y puerto:**
   - Placa: **Heltec WiFi LoRa 32(V3)**
   - Port: Puerto COM asignado (ej. COM7)
4. **Abrir el sketch:**
   - Haz doble clic sobre cualquiera de los archivos `.ino` y presiona **Subir** (Upload).
   *(Nota: si Arduino IDE arroja `PermissionError: Access is denied` en el puerto COM, desconecta y reconecta el cable USB).*

