# Diagramas Técnicos y Esquemas de Arquitectura (Estilo IEEE / Publicación)

Este directorio contiene los esquemas técnicos oficiales del Trabajo de Título:
**"Diseño, implementación y evaluación del rendimiento de una red LoRaWAN para la sensorización del Campus Dr. Luis Rivas del Canto"** (Universidad Católica de Temuco).

Todos los diagramas siguen un estándar formal académico, con paleta neutra, alineación geométrica, tipografía técnica sans-serif y flechas de interconexión explícitas adecuadas para su inclusión en la **Memoria de Título** y publicaciones IEEE.

---

## 📐 Diagramas Oficiales

Cada diagrama se encuentra disponible en 3 formatos de alta fidelidad:
- **`.pdf`**: Gráfico vectorial compacto con tipografía Helvetica incrustada, ideal para inclusión directa en LaTeX / Overleaf mediante `\includegraphics`.
- **`.png`**: Imagen rasterizada en alta definición (250 DPI) con canal alfa / fondo blanco, lista para presentaciones o visualización web.
- **`.svg`**: Gráfico vectorial escalable con trazabilidad completa de nodos, capas y flechas poligonales.

### 1. Diagrama de Arquitectura de Red Extremo a Extremo
* **Archivos:** `01_arquitectura_red.pdf` | `01_arquitectura_red.svg` | `01_arquitectura_red.png`
* **Descripción:** Representa los 3 dominios tecnológicos del prototipo optimizado:
  1. *Dominio de Radiofrecuencia:* Nodos Heltec WiFi LoRa 32 V3 (condición exterior LOS 50–200 m y condición interior NLOS 100–350 m con payload binario determinista de 10 bytes).
  2. *Dominio de Concentración y Red:* Flota de Gateways integrada por el **Milesight UG65** (Controlador con *Embedded Network Server* y concentrador SX1302 de 8 canales en AU915 SB2) y el **Milesight UG63** (Agente de extensión enlazado por *Gateway Fleet* MQTT en puerto 18883). Incluye deduplicación MAC, autenticación OTAA/AES-128 y códec integrado `decodeUplink()`, preservando ChirpStack v4 como entorno documentado de contingencia.
  3. *Dominio de Aplicación:* Broker MQTT (Mosquitto TCP 1883 / WebSocket 9001) y Dashboard Web en tiempo real.

### 2. Diagrama de Secuencia de Comunicaciones UML
* **Archivos:** `02_secuencia_otaa_uplink.pdf` | `02_secuencia_otaa_uplink.svg` | `02_secuencia_otaa_uplink.png`
* **Descripción:** Modela los flujos temporales y la interacción entre los 5 actores del sistema en 3 fases:
  1. *Fase I:* Procedimiento de adhesión por aire (OTAA Join: Join-Request $\rightarrow$ verificación MIC y derivación de llaves en el Milesight UG65 Embedded NS $\rightarrow$ Join-Accept en ventana RX1 a 923.3 MHz).
  2. *Fase II:* Sesión Tipo A con uplinks no confirmados ($NbTrans = 1$) para evaluación de tasa de pérdida de paquetes ($PL \le 10\%$) y ejecución del códec `decodeUplink()`.
  3. *Fase III:* Sesión Tipo B con uplinks confirmados y cálculo de retardo de confirmación ($T_{\text{conf}} \le 6\,\text{s}$) mediante `ACK` descendente emitido por el UG65 en ventana RX1/RX2.

### 3. Estructura del Payload Binario y Pipeline de Datos
* **Archivos:** `03_flujo_payload.pdf` | `03_flujo_payload.svg` | `03_flujo_payload.png`
* **Descripción:** Documenta la serialización y trazabilidad del dato:
  1. *Sección A:* Estructura en memoria del payload binario de 10 bytes en formato Big-Endian (Byte 0: Node ID, Bytes 1–4: Secuencia de 32 bits, Bytes 5–6: Temperatura $\times 100$, Bytes 7–8: Humedad $\times 100$, Byte 9: Tensión LiPo escalada).
  2. *Sección B:* Pipeline secuencial por capas desde el firmware C++, trama MAC física (23 bytes con Time-on-Air de 46.3 ms), recepción en flota UG65/UG63, decodificación mediante `decodeUplink()` en el Milesight UG65 Embedded NS, publicación MQTT en formato JSON y visualización en el dashboard web.

### 4. Flujo Extremo a Extremo de la Red LoRaWAN Campus UCT
* **Archivo:** `flujo_extremo_extremo_lorawan.jpg`
* **Descripción:** Infografía arquitectural que vincula la captura física de sensores DHT11 en nodos Heltec V3, modulación RF en AU915 SB2, concentración en flota con Gateway Controlador Milesight UG65 (Embedded NS) y Gateway Agente Milesight UG63, publicación MQTT hacia el broker Eclipse Mosquitto, almacenamiento en SQLite local (`telemetry.db`) y visualización en el dashboard web.

### 5. Zonificación y Plano de Cobertura Espacial
* **Archivos:** `04_despliegue_espacial_campus.jpg` | `CampusDoctorluisrivasdelcanto.png`
* **Descripción:** Imagen satelital y plano aéreo de la distribución de edificios y áreas verdes del Campus Dr. Luis Rivas del Canto (UCT), utilizado para la planificación de los puntos de medición LOS (Nodo 1, Edificio 16 - Ing. en Construcción), NLOS (Nodo 2, Edificio 08 - Dirección de Informática) y la ubicación de concentración central de gateways (Edificio 10 - Facultad de Ingeniería).
