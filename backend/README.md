# Backend y Códecs LoRaWAN - Red Campus UCT

Este directorio contiene las especificaciones y el código del códec de carga útil (payload decoder) para la recepción y deserialización de las tramas emitidas por los nodos sensores del prototipo.

---

## 1. Estructura de Payload Binario (10 Bytes Big-Endian)

Con el propósito de minimizar el tiempo en el aire (*Time on Air*, ToA $\approx 46.3\text{ ms}$) y cumplir con las regulaciones de uso eficiente del espectro radioeléctrico (SUBTEL), la telemetría se serializa en un arreglo de 10 bytes:

| Byte(s) | Campo | Tipo | Rango / Resolución | Ecuación de Decodificación |
|---|---|---|---|---|
| `0` | **Node ID** | `uint8` | 1 a 255 (`0x01`: Nodo 1, `0x02`: Nodo 2) | Identificador de nodo de origen |
| `1 – 4` | **Sequence** | `uint32` (MSB) | 0 a $4.294.967.295$ | $(B_1 \ll 24) \mid (B_2 \ll 16) \mid (B_3 \ll 8) \mid B_4$ |
| `5 – 6` | **Temperatura** | `int16` con signo | $-40.00\text{ °C}$ a $+85.00\text{ °C}$ (res. 0.01 °C) | $\text{tempRaw} / 100.0$ |
| `7 – 8` | **Humedad** | `uint16` | $0.0\,\%$ a $100.0\,\%$ (res. 0.01 %) | $\text{humRaw} / 100.0$ |
| `9` | **Batería** | `uint8` | $2.00\text{ V}$ a $4.55\text{ V}$ (paso 10 mV) | $V_{\text{bat}} = 2.0 + (\text{batRaw} / 100.0)$ |

### Estimación del Porcentaje de Batería LiPo
El porcentaje de batería se interpola linealmente sobre el rango nominal de descarga de una celda de iones de litio (3.0 V a 4.2 V):
$$\text{bat\_pct} = \min\left(100, \max\left(0, \frac{V_{\text{bat}} - 3.0}{1.2} \times 100\right)\right)$$

---

## 2. Archivo del Códec

* **[`backend/decoders/decoder.js`](decoders/decoder.js):** Función JavaScript estándar `decodeUplink(input)`.

### Ejemplo de Salida JSON
Entrada hexadecimal de 10 bytes: `01 00 00 00 1A 09 C4 17 70 8C`
```json
{
  "data": {
    "node_id": 1,
    "sequence": 26,
    "temperature": 25.00,
    "humidity": 60.0,
    "battery_mv": 3400,
    "battery_pct": 33,
    "battery_voltage": 3.40
  }
}
```

---

## 3. Guía de Configuración en Network Servers

### En Milesight UG65 (Embedded Network Server)
1. Iniciar sesión en la consola web del UG65 (`http://192.168.200.47`).
2. Ir a **Network Server** $\rightarrow$ **Device Profile**.
3. Seleccionar o editar el perfil de los dispositivos Heltec (`Heltec-V3-Profile`).
4. En la pestaña **Payload Codec**, seleccionar **Custom**.
5. Copiar y pegar el contenido íntegro de [`decoder.js`](decoders/decoder.js) en el editor.
6. Guardar cambios. El UG65 publicará automáticamente el objeto JSON decodificado bajo la clave `object` en los tópicos MQTT.

### En ChirpStack v4
1. Ir a **Device profiles** $\rightarrow$ Perfil del dispositivo.
2. En la pestaña **Codec**, seleccionar **JavaScript functions**.
3. Pegar el código de [`decoder.js`](decoders/decoder.js) dentro de la función `decodeUplink`.
4. Probar en la pestaña *Codec test* antes de guardar.

