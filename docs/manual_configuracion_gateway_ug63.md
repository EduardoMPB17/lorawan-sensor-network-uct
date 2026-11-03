# Manual de Configuración Técnica: Gateway LoRaWAN Milesight UG63
**Proyecto de Título:** Diseño, implementación y evaluación del rendimiento de una red LoRaWAN para la sensorización del Campus Dr. Luis Rivas del Canto  
**Institución:** Universidad Católica de Temuco (UCT) — Facultad de Ingeniería  
**Hardware:** Milesight UG63 Mini LoRaWAN Gateway (`UG63-L08GL-915M`)  

---

## 1. Identificación y Parámetros de Fábrica

A partir de la etiqueta de identificación del equipo:
* **Modelo Exacto:** `UG63-L08GL-915M`
* **Gateway EUI (Obligatorio para ChirpStack):** `C0BA1FFFFE0377FA`
* **Dirección MAC Ethernet:** `C0:BA:1F:03:77:FA`
* **Número de Serie (SN):** `6739059F52A70000`
* **Chipset LoRa Baseband:** Semtech SX1302 (8 canales concurrentes)
* **IP Estática de Fábrica (Puerto LAN Ethernet):** `192.168.23.150`
* **Credenciales de Fábrica:**
  * **Usuario:** `admin`
  * **Contraseña inicial:** `password`

---

## 2. Conexión Física y Energización

1. **Alimentación Eléctrica:**
   * **Opción A (Laboratorio / Banco de Pruebas):** Conectar un cable USB Type-C ($5\,\text{V} / 1\,\text{A}$) al puerto Type-C del gateway desde un cargador convencional o puerto USB del computador.
   * **Opción B (Despliegue Institucional):** Conectar el cable Ethernet RJ45 a un switch o inyector PoE bajo estándar **IEEE 802.3af**. El equipo se alimentará y transmitirá datos por el mismo cable.
2. **LED de Estado:**
   * **LED SYS (Sistema):** Parpadea lentamente durante el arranque y queda en verde fijo cuando el sistema operativo interno está listo (~40 segundos).
   * **LED LoRa:** Se ilumina al inicializar el concentrador SX1302 y parpadea brevemente cuando recibe/transmite tramas de radiofrecuencia.

---

## 3. Primer Acceso a la Interfaz Web (Web GUI)

### Paso 3.1: Configuración de Red en el Computador
Para conectarse directamente por cable de red desde el PC al gateway:
1. Conectar un cable de red RJ45 entre el puerto Ethernet del computador y el puerto del UG63.
2. En Windows, abrir **Configuración de red e Internet** $\rightarrow$ **Cambiar opciones del adaptador**.
3. Clic derecho en el adaptador Ethernet $\rightarrow$ **Propiedades** $\rightarrow$ doble clic en **Protocolo de Internet versión 4 (TCP/IPv4)**.
4. Asignar una IP estática dentro del segmento `192.168.23.x`:
   * **Dirección IP:** `192.168.23.100`
   * **Máscara de subred:** `255.255.255.0`
   * **Puerta de enlace predeterminada:** `192.168.23.150`
5. Guardar los cambios.

### Paso 3.2: Acceso por Navegador
1. Abrir Google Chrome, Edge o Firefox.
2. Ingresar la URL:
   ```text
   https://192.168.23.150
   ```
3. El navegador mostrará una advertencia de seguridad (*"La conexión no es privada"* o certificado autofirmado). Hacer clic en **Configuración avanzada** $\rightarrow$ **Continuar a 192.168.23.150 (no seguro)**.
4. Ingresar las credenciales:
   * **Username:** `admin`
   * **Password:** `password`
5. **Cambio obligatorio de contraseña:** En el primer inicio, el sistema solicitará definir una nueva contraseña de administrador. Establecer una contraseña segura y documentarla en la bitácora del proyecto.

---

## 4. Configuración de Radiofrecuencia (Banda AU915 / SUBTEL Chile)

Para cumplir con la **Resolución Exenta 1.985 de la SUBTEL** y coordinar con los nodos sensores **Heltec V3 (RadioLib)**:

1. En el menú de navegación izquierdo, ir a **Packet Forwarder** $\rightarrow$ **Radio**.
2. **Region:** Seleccionar **`AU915`** (Banda 915–928 MHz).
3. **Channel Plan / Sub-band:**
   * Seleccionar **Sub-band 2** (canales 8 al 15):
     * **Canal 8:** 916.8 MHz (BW 125 kHz)
     * **Canal 9:** 917.0 MHz (BW 125 kHz)
     * **Canal 10:** 917.2 MHz (BW 125 kHz)
     * **Canal 11:** 917.4 MHz (BW 125 kHz)
     * **Canal 12:** 917.6 MHz (BW 125 kHz)
     * **Canal 13:** 917.8 MHz (BW 125 kHz)
     * **Canal 14:** 918.0 MHz (BW 125 kHz)
     * **Canal 15:** 918.2 MHz (BW 125 kHz)
     * **Canal Uplink 500 kHz (Canal 65):** 917.5 MHz
   * **Frecuencias Downlink (RX1):** 923.3 MHz a 927.5 MHz.
   * **Parámetros RX2 por defecto:**
     * **Frecuencia:** `923.3 MHz`
     * **Data Rate:** `DR8` (SF12 / BW 500 kHz).
4. **Potencia de Transmisión (TX Power):**
   * Configurar a un máximo de **14 dBm** (25 mW e.i.r.p.) para asegurar estricto cumplimiento normativo en el campus.
5. Hacer clic en **Save** y luego en **Apply**.

---

## 5. Integración con el Servidor de Red (ChirpStack v4)

El UG63 reenvía los paquetes capturados por radio hacia el servidor central ChirpStack mediante el protocolo estándar **Semtech UDP Packet Forwarder**.

### Paso 5.1: Configuración en la Web GUI del Gateway
1. En el menú izquierdo, ir a **Packet Forwarder** $\rightarrow$ **General**.
2. Verificar que el **Gateway EUI** mostrado en pantalla sea exactamente:
   ```text
   C0BA1FFFFE0377FA
   ```
3. En la sección **Server Settings**:
   * **Enable:** Marcar la casilla / Switch en `ON`.
   * **Type:** Seleccionar **Semtech UDP Forwarder**.
   * **Server Address:** Ingresar la dirección IP del servidor donde corre ChirpStack (por ejemplo, `192.168.1.50` o la IP interna de la facultad).
   * **Port Up:** `1700` (puerto estándar de recepción de uplinks en `chirpstack-gateway-bridge`).
   * **Port Down:** `1700` (puerto de downlinks/ACKs).
4. Hacer clic en **Save** y **Apply**.

---

## 6. Registro del Gateway en ChirpStack

Una vez configurado el gateway, se debe dar de alta en la consola de gestión de ChirpStack:

1. Abrir la interfaz web de ChirpStack en el navegador (`http://<IP_SERVIDOR>:8080`).
2. Iniciar sesión y seleccionar el **Tenant** del proyecto (ej. `UCT-LoRaWAN`).
3. En el menú lateral, seleccionar **Gateways** $\rightarrow$ botón **Add gateway**.
4. Completar los campos con los datos del UG63:
   * **Name:** `UG63-Campus-Luis-Rivas` (o nombre formal institucional).
   * **Description:** `Milesight UG63 Mini LoRaWAN Gateway SX1302 8-ch (Facultad de Ingeniería)`.
   * **Gateway EUI:** Ingresar en minúsculas o mayúsculas sin guiones:
     ```text
     c0ba1ffffe0377fa
     ```
   * **Stats interval (seconds):** `30`.
5. Hacer clic en **Submit**.
6. **Verificación de conexión:** En la lista de Gateways de ChirpStack, observar la columna **Last seen**. En menos de 30 segundos debe marcar *"Online"* o *"a few seconds ago"*.

---

## 7. Monitoreo y Validación de Tráfico en Tiempo Real

Para verificar que los nodos **Heltec WiFi LoRa 32 V3** están siendo escuchados:

### Verificación en el Gateway (Local):
1. En la Web GUI del UG63, ir a **Packet Forwarder** $\rightarrow$ **Traffic**.
2. Al encender un nodo emisor, aparecerá una fila en la tabla con:
   * **Time:** Marca de tiempo.
   * **Freq:** Frecuencia de recepción (ej. `916.80 MHz`).
   * **Data Rate:** SF7 a SF10 según configuración.
   * **RSSI:** Intensidad de señal recibida (ej. `-75 dBm`).
   * **SNR:** Relación señal/ruido (ej. `+9.5 dB`).
   * **Payload:** Cadena hexadecimal correspondiente al frame LoRaWAN.

### Verificación en ChirpStack:
1. En ChirpStack, ir a **Gateways** $\rightarrow$ seleccionar el gateway $\rightarrow$ pestaña **LoRaWAN frames**.
2. Aquí se visualizarán las solicitudes de unión (**Join Request**) y los paquetes de telemetría periódica (**UnconfirmedDataUp** / **ConfirmedDataUp**) con sus métricas RF asociadas.

---

## 8. Modo de Contingencia: Network Server Embebido

Si por razones de mantenimiento en la red de la UCT no se tiene acceso al servidor ChirpStack externo:
1. El UG63 incluye su propio **Embedded Network Server**.
2. Se activa en **LoRaWAN** $\rightarrow$ **Network Server** $\rightarrow$ **Enable**.
3. Permite dar de alta las aplicaciones, llaves OTAA (`AppEUI`, `AppKey`) y publicar la telemetría directamente a un **Broker MQTT local** (ej. Mosquitto) en el puerto `1883`, garantizando que las pruebas de campo de la tesis nunca se detengan.
