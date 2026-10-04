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
* **Descripción:** Representa los 3 dominios tecnológicos del prototipo:
  1. *Dominio de Radiofrecuencia:* Nodos Heltec WiFi LoRa 32 V3 (condición exterior LOS 50–200 m y condición interior NLOS 100–350 m con payload binario de 10 bytes).
  2. *Dominio de Concentración y Red:* Gateway LoRaWAN multicanal (AU915 SB2) con Packet Forwarder UDP (puerto 1700) enlazado a Servidor de Red ChirpStack v4 local (codec `decoder.js` y derivación de claves OTAA).
  3. *Dominio de Aplicación:* Broker MQTT (Mosquitto TCP 1883 / WebSocket 9001) y Dashboard Web en tiempo real.

### 2. Diagrama de Secuencia de Comunicaciones UML
* **Archivos:** `02_secuencia_otaa_uplink.pdf` | `02_secuencia_otaa_uplink.svg` | `02_secuencia_otaa_uplink.png`
* **Descripción:** Modela los flujos temporales y la interacción entre los 5 actores del sistema en 3 fases:
  1. *Fase I:* Procedimiento de adhesión por aire (OTAA Join: Join-Request $\rightarrow$ Join-Accept en ventana RX1 a 923.3 MHz).
  2. *Fase II:* Sesión Tipo A con uplinks no confirmados ($NbTrans = 1$) para evaluación de tasa de pérdida de paquetes ($PL \le 10\%$).
  3. *Fase III:* Sesión Tipo B con uplinks confirmados y cálculo de retardo de confirmación ($T_{\text{conf}} \le 6\,\text{s}$).

### 3. Estructura del Payload Binario y Pipeline de Datos
* **Archivos:** `03_flujo_payload.pdf` | `03_flujo_payload.svg` | `03_flujo_payload.png`
* **Descripción:** Documenta la serialización y trazabilidad del dato:
  1. *Sección A:* Estructura en memoria del payload binario de 10 bytes en formato Big-Endian (Byte 0: Node ID, Bytes 1–4: Secuencia, Bytes 5–6: Temperatura $\times 100$, Bytes 7–8: Humedad $\times 100$, Byte 9: Voltaje LiPo escalado).
  2. *Sección B:* Pipeline secuencial por capas desde el firmware C++, trama MAC física (23 bytes con Time-on-Air de 46.3 ms), decodificación en ChirpStack v4, publicación MQTT en formato JSON y visualización en el dashboard web.
