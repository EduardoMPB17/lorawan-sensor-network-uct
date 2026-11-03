# Prototipo de Red LoRaWAN Intra-Campus - UCT

Este repositorio contiene el código fuente, esquemas de integración, diagramas de arquitectura y documentación técnica del Trabajo de Título:  
**"Diseño, implementación y evaluación del rendimiento de una red LoRaWAN para la sensorización del Campus Dr. Luis Rivas del Canto"**, desarrollado en la carrera de Ingeniería Civil Informática de la Universidad Católica de Temuco (UCT).

* **Autor:** Eduardo Remigio Mariqueo Porma
* **Profesor Guía:** Mg. Mario Villanueva Alveal (Jefe de Carrera ICI)

---

## 1. Arquitectura del Sistema Desplegado

El prototipo implementa una topología celular/estrella multi-gateway bajo el estándar **LoRaWAN 1.0.4** en la banda regional **AU915 Sub-banda 2** (916.8 – 918.2 MHz, con enlace de bajada RX2 en 923.3 MHz):

* **Dominio de Percepción (Nodos Sensores):**
  - Módulos **Heltec WiFi LoRa 32 V3** (ESP32-S3 + Semtech SX1262).
  - Sensor de temperatura y humedad **DHT11** conectado a **GPIO 4**.
  - Pantalla OLED SSD1306 (I2C) para diagnóstico local en terreno (tensión, conteo, ToA, ACK).
  - Potencia de emisión: **14 dBm (25 mW)** conforme a la normativa SUBTEL (Res. Exenta N.º 1.985/2017 y N.º 737/2025).
  - Modulación LoRa DR5 (SF7 / BW 125 kHz) $\rightarrow$ Time on Air (ToA) $\approx 46.3\text{ ms}$.

* **Dominio de Red y Concentración (Gateways):**
  - **Gateway Controlador:** **Milesight UG65** (IP `192.168.200.47`), concentrador SX1302 con **Embedded Network Server** activo y servicio **Gateway Fleet**. Autentica dispositivos, gestiona las claves OTAA y deduplica tramas.
  - **Gateway Agente:** **Milesight UG63** (IP `192.168.200.30`), concentrador SX1302 en modo **Remoted Embedded NS** reenviando paquetes RF al UG65 mediante protocolo MQTT por el **puerto 18883**.

* **Dominio de Aplicación y Telemetría:**
  - Broker **Eclipse Mosquitto** en host local (`192.168.200.45:1883`).
  - **Servidor y Dashboard Web:** [`dashboard/dashboard_server.py`](dashboard/dashboard_server.py) (puerto HTTP 5000) con persistencia en SQLite (`telemetry.db`), visualización en tiempo real y capturador automatizado de sesiones de prueba.

---

## 2. Objetivos y Métricas SMART (Calidad de Servicio)

| Métrica | Requerimiento | Modo Experimental | Definición Operacional |
|---|---|---|---|
| **RQS1 Packet Loss** | $PL \le 10\,\%$ ($PDR \ge 90\,\%$) | **Sesión Tipo A** | 100 tramas no confirmadas, $\text{NbTrans} = 1$, intervalo controlado |
| **RQS2 Retardo de Confirmación** | $T_{\text{conf}} \le 6.0\text{ s}$ | **Sesión Tipo B** | $\ge 30$ tramas confirmadas; mide $T_{\text{conf}} = T_{\text{ACK}} - T_{\text{env}}$ vía `millis()` en RX1/RX2 |
| **RQS3 Disponibilidad** | $A \ge 90\,\%$ | Operación continua | Ratio de tiempo operativo y tasa de recepción global |

---

## 3. Dispositivos Registrados

| Identificador | Rol Experimental | DevEUI | Primer Byte Payload | Registro UG65 |
|---|---|---|---|---|
| **Nodo 1** | Línea de Vista (LOS) | `0102030405060708` | `0x01` | `Heltec-V3-Nodo1` |
| **Nodo 2** | Obstruido (NLOS) | `0102030405060709` | `0x02` | `Heltec-V3-Nodo2` |

* **JoinEUI común:** `0000000000000000`
* **AppKey común:** `2B7E151628AED2A6ABF7158809CF4F3C`

---

## 4. Estructura del Repositorio

```text
lorawan-sensor-network-uct/
├── backend/
│   ├── README.md                # Documentación del payload de 10 B y ecuaciones
│   └── decoders/
│       └── decoder.js           # Decodificador JavaScript oficial (Milesight / ChirpStack)
├── dashboard/
│   ├── dashboard_server.py      # Servidor HTTP + cliente MQTT + SQLite + UI web en vivo
│   └── README.md                # Manual de uso y ejecución del dashboard
├── docs/
│   ├── manual_configuracion_gateway_ug63.md # Guía paso a paso de integración UG63 -> UG65
│   ├── diagramas/               # Diagramas oficiales en formatos PDF, PNG y SVG
│   │   ├── 01_arquitectura_red.*
│   │   ├── 02_secuencia_otaa_uplink.*
│   │   ├── 03_flujo_payload.*
│   │   ├── CampusDoctorluisrivasdelcanto.png
│   │   └── README.md
│   └── informes/                # Fuentes LaTeX de informes académicos de avance
├── firmware/
│   ├── sesion-tipo-a/           # Tramas no confirmadas para medir Packet Loss (PL <= 10%)
│   │   ├── nodo1_heltec_v3_tipoA/
│   │   └── nodo2_heltec_v3_tipoA/
│   ├── sesion-tipo-b/           # Tramas confirmadas para medir Retardo T_conf (<= 6.0 s)
│   │   ├── nodo1_heltec_v3_tipoB/
│   │   └── nodo2_heltec_v3_tipoB/
│   └── README.md                # Guía de flasheo y configuración de pines en Arduino IDE
└── scripts/
    ├── bridge_cloud.py          # Puente MQTT local hacia broker público EMQX
    ├── monitor_lorawan.py       # Monitor de consola en tiempo real
    └── README.md                # Instrucciones de ejecución de herramientas CLI
```

---

## 5. Instrucciones Rápidas de Puesta en Marcha

1. **Flashear Nodos Sensores:**
   - Abrir Arduino IDE y compilar el sketch correspondiente en [`firmware/`](firmware/):
     - Para medir pérdidas de paquetes (RQS1): [`sesion-tipo-a/`](firmware/sesion-tipo-a/)
     - Para medir retardos con confirmación ACK (RQS2): [`sesion-tipo-b/`](firmware/sesion-tipo-b/)
2. **Configurar Códec en el Network Server:**
   - Copiar [`backend/decoders/decoder.js`](backend/decoders/decoder.js) en el perfil de dispositivo de la consola del Milesight UG65.
3. **Iniciar Servidor de Telemetría:**
   ```bash
   pip install paho-mqtt
   cd dashboard
   python dashboard_server.py
   ```
   Acceder a `http://localhost:5000` para monitorización en vivo y captura de datasets.
