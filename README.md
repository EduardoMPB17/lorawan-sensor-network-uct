# Prototipo de Red LoRaWAN Intra-Campus - UCT

Este repositorio contiene el código fuente, esquemas de integración y documentación técnica del Trabajo de Título:  
**"Diseño, implementación y evaluación del rendimiento de una red LoRaWAN para la sensorización del Campus Dr. Luis Rivas del Canto"**, desarrollado en la Escuela de Ingeniería Informática de la Universidad Católica de Temuco.

## Arquitectura del Sistema
El prototipo implementa una topología estrella sobre el estándar LoRaWAN en la banda regional AU915:
- **Nodos Sensores:** Módulos Heltec WiFi LoRa 32 (ESP32 + Semtech SX1262/SX1276) transmitiendo telemetría con activación OTAA.
- **Gateway Central:** Concentrador multicanal institucional ubicado en la Facultad de Ingeniería.
- **Network Server:** Instancia ChirpStack procesando tramas de enlace ascendente (uplink).
- **Broker MQTT:** Distribución y enrutamiento de datos formateados en JSON.
- **Dashboard:** Interfaz de visualización simple para monitorización en tiempo real.

## Estructura del Repositorio
```text
├── backend/          # Configuración del Network Server y codecs de decodificación
├── dashboard/        # Interfaz web o flujo de Node-RED para visualización
├── docs/             # Diagramas de arquitectura, memorias y guías de configuración
├── firmware/         # Código fuente en C/C++ para los nodos sensores Heltec
└── scripts/          # Automatización de pruebas, logs de tráfico y análisis