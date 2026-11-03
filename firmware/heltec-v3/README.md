# Firmware Oficial Heltec WiFi LoRa 32 V3 - Red Campus UCT

Este directorio contiene el código fuente en C/C++ (sketches Arduino `.ino`) para los nodos sensores del prototipo LoRaWAN desplegado en el **Campus Dr. Luis Rivas del Canto**, Universidad Católica de Temuco.

---

## 1. Plataforma de Hardware

* **Módulo:** Heltec WiFi LoRa 32 V3 (SoC Espressif ESP32-S3FN8 dual-core Xtensa LX7 + transceptor Semtech SX1262).
* **Sensor:** DHT11 (temperatura y humedad relativa).
* **Pantalla:** OLED monocromática 0.96" SSD1306 (128x64 píxeles, interfaz I2C).

### Mapeo de Conexiones Físicas
| Componente | Señal | Pin ESP32-S3 | Observaciones |
|---|---|---|---|
| **DHT11** | DATA | **GPIO 4** | Conexión directa sin protoboard (alimentación a 3V3 y GND) |
| **OLED** | SDA | **GPIO 17** | Bus I2C interno |
| **OLED** | SCL | **GPIO 18** | Bus I2C interno |
| **OLED / Periféricos** | RST | **GPIO 21** | Reset de pantalla |
| **Alimentación Vext** | Control | **GPIO 36** | **Activo en LOW** (energiza el riel del SX1262 y la pantalla) |
| **LED Usuario** | Ánodo | **GPIO 35** | Indicador lumínico de estado |
| **SX1262** | NSS / CS | **GPIO 8** | Selección de chip SPI |
| **SX1262** | RST | **GPIO 12** | Reset del transceptor |
| **SX1262** | BUSY | **GPIO 13** | Indicador de estado de radio |
| **SX1262** | DIO1 | **GPIO 14** | Interrupción IRQ (Tx/Rx Done) |

> [!CAUTION]
> **Regla de Hardware RT2:** **NUNCA** energizar la placa Heltec sin tener conectada su antena omnidireccional de 915 MHz (+2 dBi). La ausencia de carga en el conector U.FL provoca ondas estacionarias de alta reflectancia que pueden destruir irreparablemente el amplificador de potencia (PA) del chip SX1262.

---

## 2. Parámetros de RF y Regulación SUBTEL

* **Plan de Frecuencias:** Regional AU915, **Sub-banda 2** (Canales 8 a 15, 916.8 MHz – 918.2 MHz).
* **Ventana RX2 Downlink:** Frecuencia fija 923.3 MHz, DR8 (SF12 / 500 kHz).
* **Potencia de Transmisión:** **14 dBm (25 mW)** (conforme a Resolución Exenta N.º 1.985/2017 y N.º 737/2025 de SUBTEL).
* **Datarate de Uplink:** DR5 (SF7 / BW 125 kHz).
* **Time on Air (ToA):** ~46.3 ms por trama (payload de 10 B, 23 B a nivel físico con cabeceras LoRaWAN + MIC).

---

## 3. Dispositivos y Credenciales OTAA

* **JoinEUI (AppEUI):** `0000000000000000`
* **AppKey (común):** `2B 7E 15 16 28 AE D2 A6 AB F7 15 88 09 CF 4F 3C`

| Nodo | Rol Experimental | DevEUI | Primer Byte Payload (`node_id`) | Nombre en NS UG65 |
|---|---|---|---|---|
| **Nodo 1** | LOS (Línea de Vista) | `0102030405060708` | `0x01` | `Heltec-V3-Nodo1` |
| **Nodo 2** | NLOS (Obstruido / Shadowing) | `0102030405060709` | `0x02` | `Heltec-V3-Nodo2` |
| **Nodo 3** | Expansión de Cobertura | `010203040506070A` | `0x03` | `Heltec-V3-Nodo3B` |

> [!IMPORTANT]
> Cada nodo físico debe disponer de un **DevEUI único**. El reuso de DevEUI invalida la sesión de cifrado OTAA (desfase de claves de sesión NwkSKey/AppSKey) y rompe los contadores anti-replay `fCntUp`.

---

## 4. Estructura de Payload Binario (10 Bytes Big-Endian)

```
+------------+----------------------+--------------------+-------------------+---------------------+
| Byte 0     | Bytes 1-4            | Bytes 5-6          | Bytes 7-8         | Byte 9              |
| Node ID    | Sequence (FCnt)      | Temp * 100         | Hum * 100         | (Vbat - 2.0) * 100  |
| uint8_t    | uint32_t (MSB first) | int16_t (MSB first)| uint16_t (MSB)    | uint8_t             |
+------------+----------------------+--------------------+-------------------+---------------------+
```

---

## 5. Organización del Código

```text
firmware/heltec-v3/
├── sesion-tipo-a/                       # Tramas no confirmadas para medir Packet Loss (PL <= 10%)
│   ├── nodo1_heltec_v3_dht11/           # Firmware Nodo 1 (LOS)
│   │   └── nodo1_heltec_v3_dht11.ino
│   └── nodo2_heltec_v3_dht11/           # Firmware Nodo 2 (NLOS)
│       └── nodo2_heltec_v3_dht11.ino
├── sesion-tipo-b/                       # Tramas confirmadas para medir Retardo T_conf (<= 6.0 s)
│   ├── nodo1_heltec_v3_sesion_tipoB/    # Firmware Nodo 1 (LOS)
│   │   └── nodo1_heltec_v3_sesion_tipoB.ino
│   ├── nodo2_heltec_v3_sesion_tipoB/    # Firmware Nodo 2 (NLOS)
│   │   └── nodo2_heltec_v3_sesion_tipoB.ino
│   └── nodo3_heltec_v3_sesion_tipoB/    # Firmware Nodo 3 (Expansión)
│       └── nodo3_heltec_v3_sesion_tipoB.ino
└── pruebas/
    └── nodo_prueba_heltec_v3_lorawan/   # Sketch mínimo de prueba OTAA
        └── nodo_prueba_heltec_v3_lorawan.ino
```

### Librerías Requeridas en Arduino IDE
* `RadioLib` (v6.0 o superior)
* `Adafruit SSD1306`
* `Adafruit GFX Library`
* `Adafruit DHT sensor library`

