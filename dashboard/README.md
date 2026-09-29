# Dashboard Web de Visualización Simple - Red LoRaWAN UCT

Este dashboard web cumple con el **Requerimiento Funcional RF4** y las especificaciones de la **Épica 3** del Trabajo de Título:
> *"El dashboard de visualización simple debe identificar el nodo sensor de origen y mostrar, como mínimo, identificador, marca temporal y valor medido, sin incorporar analítica avanzada."*

---

## Características Principales

1. **Monitoreo Diferenciado por Condición de Enlace:**
   * **Nodo 1 (LOS - Exterior):** Con línea de vista directa hacia el Gateway (50–200 m).
   * **Nodo 2 (NLOS - Obstrucción Parcial):** Atenuación por muros y estructura de hormigón (100–350 m), fundamentado en el modelo Log-Distance de propagación.
2. **Variables de Telemetría en Tiempo Real:**
   * Temperatura ambiente (°C).
   * Humedad relativa (% RH).
   * Nivel y porcentaje de batería LiPo (V).
   * Número de secuencia de trama (#).
   * Métricas de canal: **RSSI** (dBm) y **SNR** (dB).
3. **Control de Disponibilidad en Línea (RQS3):**
   * Detecta caídas automáticamente si $\Delta t > 3 \cdot T_{\text{periodo}}$ (180 segundos sin recibir tramas).
4. **Gráficas de Evolución Temporal:**
   * Curvas de temperatura y humedad en Chart.js.
   * Gráfica comparativa de atenuación de señal (RSSI y SNR).
5. **Historial y Exportación:**
   * Tabla interactiva con cabeceras fijas (*sticky headers*).
   * Botón de descarga de dataset a archivo `.csv` para análisis en la Etapa 3.
6. **Modos de Operación:**
   * **Modo Simulación:** Activo por defecto para pruebas y demostraciones inmediatas sin hardware conectado.
   * **Modo MQTT en Vivo:** Conexión directa mediante WebSockets a un Broker MQTT (Mosquitto o ChirpStack).

---

## Cómo Ejecutar el Dashboard

### Opción 1: Abrir directamente en el navegador
Haz doble clic sobre el archivo [`index.html`](file:///c:/Users/Administrador/Desktop/Tesis/lorawan-sensor-network-uct/dashboard/index.html) o ábrelo con Google Chrome / Microsoft Edge.

### Opción 2: Servidor web local ligero (Python)
Desde la terminal en este repositorio:
```bash
python -m http.server 8080 --directory dashboard
```
Luego abre tu navegador en `http://localhost:8080`.
