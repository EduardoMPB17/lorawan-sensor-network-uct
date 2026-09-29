# Firmware LoRaWAN Oficial - Nodo Emisor Heltec WiFi LoRa 32 V3

Este directorio contiene el firmware definitivo para los nodos sensores del prototipo LoRaWAN del **Campus Dr. Luis Rivas del Canto (UCT)**, desarrollado bajo la metodología PPDIOO y los requerimientos RF1, RF5, RT1-RT3, RQS1-RQS3.

---

## 1. Hardware y Conectividad
* **Dispositivo:** Heltec WiFi LoRa 32 V3 (ESP32-S3FN8 + Semtech SX1262).
* **Mapeo de Pines SX1262:**
  * NSS / CS: `GPIO 8`
  * DIO1 (IRQ): `GPIO 14`
  * RST: `GPIO 12`
  * BUSY: `GPIO 13`
  * VEXT (Control bus de periféricos / RF): `GPIO 36` (**Activo en LOW**)
  * ADC Batería: `GPIO 1` (Habilitación del divisor resistivo: `GPIO 37` en LOW)
* **Regla de Hardware RT2:** **OBLIGATORIO** conectar la antena de 915 MHz antes de energizar la placa para evitar daños térmicos/eléctricos irreparables en la etapa de potencia RF del SX1262.

---

## 2. Parámetros LoRaWAN y Marco Regulatorio
* **Banda:** AU915 (915 a 928 MHz), conforme a la Resolución Exenta N.º 1.985 de SUBTEL.
* **Sub-banda:** Sub-banda 2 (Canales 8 a 15, Uplink 916.8 a 918.2 MHz).
* **Potencia máxima de emisión:** 14 dBm (`radio.setOutputPower(14)`).
* **Datarate:** DR5 (SF7 / BW 125 kHz) con ADR deshabilitado para garantizar condiciones controladas y reproducibles.
* **Activación:** OTAA (Over-the-Air Activation) bajo especificación LoRaWAN 1.0.4.

---

## 3. Modos de Sesión Experimental
En [`config.h`](file:///c:/Users/Administrador/Desktop/Tesis/lorawan-sensor-network-uct/firmware/nodo-emisor/config.h), selecciona el tipo de sesión modificando la macro:
```c
#define CURRENT_SESSION_MODE  SESSION_TYPE_A  // Para medir Packet Loss (PL <= 10%)
// o
#define CURRENT_SESSION_MODE  SESSION_TYPE_B  // Para medir Retardo T_conf (<= 6 s)
```
* **Sesión Tipo A:** Uplinks no confirmados (`isConfirmed = false`, `NbTrans = 1`), 100 tramas por sesión, periodo $T_{\text{periodo}} = 60\text{ s}$.
* **Sesión Tipo B:** Uplinks confirmados (`isConfirmed = true`), $\ge 30$ tramas por sesión. El firmware mide internamente el tiempo de ida y vuelta (round-trip time) hasta la llegada del ACK en ventanas RX1 o RX2.

---

## 4. Registro en ChirpStack v4
1. En la consola web de ChirpStack, crea una aplicación (ej. `UCT-Campus-LoRaWAN`).
2. Crea un **Device Profile** con:
   * **Region:** `AU915`
   * **MAC version:** `1.0.4`
   * **Regional parameters revision:** `RP002-1.0.4`
   * **ADR algorithm:** Default
3. Registra el dispositivo con el `DevEUI`, `JoinEUI` y `AppKey` configurados en [`config.h`](file:///c:/Users/Administrador/Desktop/Tesis/lorawan-sensor-network-uct/firmware/nodo-emisor/config.h).
4. Copia el codec de [`backend/decoders/decoder.js`](file:///c:/Users/Administrador/Desktop/Tesis/lorawan-sensor-network-uct/backend/decoders/decoder.js) en la pestaña *Codec* de ChirpStack.
