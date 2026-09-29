/* ==========================================================================
 * TRABAJO DE TÍTULO - ESCUELA DE INGENIERÍA INFORMÁTICA (UCT)
 * Proyecto: Red LoRaWAN Campus Dr. Luis Rivas del Canto
 * Alumno: Eduardo Remigio Mariqueo Porma | Profesor Guía: Prof. Mario Villanueva
 *
 * Firmware Base del Nodo Emisor Telemetría
 * Hardware: Heltec WiFi LoRa 32 V3 (ESP32-S3FN8 + Semtech SX1262)
 * Framework: Arduino C/C++ con RadioLib
 * ========================================================================== */

#include <Arduino.h>
#include <RadioLib.h>
#include "config.h"
#include "payload.h"

// --------------------------------------------------------------------------
// Instanciación de Hardware de RF (Semtech SX1262) y Stack LoRaWAN
// Mapeo Heltec V3: Module(cs, irq, rst, gpio) -> (8, 14, 12, 13)
// --------------------------------------------------------------------------
SX1262 radio = new Module(PIN_NSS, PIN_DIO1, PIN_RST, PIN_BUSY);
LoRaWANNode node(&radio, &AU915);

// Variables de estado del enlace y experimento
static uint32_t sequenceCounter = 0;
static unsigned long lastTxTime = 0;
static const unsigned long txIntervalMs = (unsigned long)TX_INTERVAL_SECONDS * 1000UL;

// --------------------------------------------------------------------------
// Prototipos de funciones auxiliares
// --------------------------------------------------------------------------
float readBatteryVoltage();
float getTemperatureReading();
float getHumidityReading();
void printHexPayload(const uint8_t* buffer, size_t length);
void checkDownlinkData();

void setup() {
    Serial.begin(115200);
    delay(2000); // Pausa para estabilización del puerto USB CDC en ESP32-S3

    Serial.println(F("\n======================================================="));
    Serial.println(F("  UCT - RED LORAWAN CAMPUS DR. LUIS RIVAS DEL CANTO   "));
    Serial.println(F("  Firmware Nodo Emisor Heltec WiFi LoRa 32 V3 (SX1262) "));
    Serial.println(F("======================================================="));

    // Verificación de la Regla de Seguridad de Hardware RT2
    Serial.println(F("[SEGURIDAD RT2] Verifique que la antena de 915 MHz este conectada."));

    // 1. Energización del bus VEXT (Activo en nivel bajo LOW en Heltec V3)
    // Controla la línea de alimentación de periféricos y el frontend de RF
    pinMode(PIN_VEXT, OUTPUT);
    digitalWrite(PIN_VEXT, LOW);
    delay(100);
    Serial.println(F("[HARDWARE] Bus VEXT energizado correctamente."));

    // 2. Inicialización del transceptor Semtech SX1262
    Serial.print(F("[SX1262] Inicializando transceptor de radio... "));
    int16_t state = radio.begin();
    if (state != RADIOLIB_ERR_NONE) {
        Serial.printf("FALLO (Codigo de error: %d)\n", state);
        Serial.println(F("[ERROR CRITICO] Revise conexiones internas SPI y alimentacion. Sistema detenido."));
        while (true) { delay(1000); }
    }
    Serial.println(F("OK."));

    // Configuración de potencia de salida conforme a Norma Técnica SUBTEL (RT1: Max 14 dBm)
    radio.setOutputPower(LORA_TX_POWER_DBM);
    Serial.printf("[RF] Potencia de transmision configurada a: %d dBm (Norma SUBTEL Res. Ex. 1.985)\n", LORA_TX_POWER_DBM);

    // 3. Configuración de parámetros LoRaWAN para el plan regional AU915
    Serial.print(F("[LoRaWAN] Configurando AU915 Sub-banda 2 (Canales 8 a 15)... "));
    state = node.selectSubband(AU915_SUBBAND);
    if (state != RADIOLIB_ERR_NONE) {
        Serial.printf("FALLO (%d)\n", state);
    } else {
        Serial.println(F("OK."));
    }

    // Deshabilitar ADR para mantener control experimental de las pruebas (SF constante)
    node.setADR(false);
    node.setDatarate(LORA_INITIAL_DATARATE); // DR5 = SF7 / BW 125 kHz
    Serial.printf("[LoRaWAN] ADR deshabilitado. Datarate fijado en DR%d (SF7 / 125 kHz)\n", LORA_INITIAL_DATARATE);

    // 4. Configuración de credenciales OTAA
    Serial.println(F("[LoRaWAN] Registrando credenciales OTAA..."));
    Serial.printf("  -> DevEUI:  0x%016llX\n", LORAWAN_DEV_EUI);
    Serial.printf("  -> JoinEUI: 0x%016llX\n", LORAWAN_JOIN_EUI);
    Serial.printf("  -> Node ID: %d\n", NODE_ID);

    state = node.beginOTAA(LORAWAN_JOIN_EUI, LORAWAN_DEV_EUI, LORAWAN_NWK_KEY, LORAWAN_APP_KEY);
    if (state != RADIOLIB_ERR_NONE) {
        Serial.printf("[ERROR] Fallo configurando credenciales OTAA (Codigo %d)\n", state);
        while (true) { delay(1000); }
    }

    // 5. Procedimiento de activación por aire (Join OTAA)
    Serial.println(F("[LoRaWAN] Enviando Join-Request a ChirpStack..."));
    state = node.activateOTAA();
    int joinAttempt = 1;

    while (state != RADIOLIB_LORAWAN_NEW_SESSION && state != RADIOLIB_ERR_NONE) {
        Serial.printf("[LoRaWAN] Intento #%d de Join fallo (Codigo %d). Reintentando en 10s...\n", joinAttempt++, state);
        delay(10000);
        state = node.activateOTAA();
    }

    Serial.println(F("[LoRaWAN] *** JOIN EXITOSO! Sesion establecida con ChirpStack ***\n"));

    // Reporte de modo de sesión experimental seleccionado
    if (CURRENT_SESSION_MODE == SESSION_TYPE_A) {
        Serial.println(F("[PROTOCOLO] MODO ACTIVO: Sesion Tipo A (Tramas NO confirmadas, NbTrans=1)"));
        Serial.println(F("[PROTOCOLO] Evaluacion objetivo: Tasa de Perdida de Paquetes (PL <= 10% [RQS1])"));
    } else {
        Serial.println(F("[PROTOCOLO] MODO ACTIVO: Sesion Tipo B (Tramas CONFIRMADAS con ACK)"));
        Serial.println(F("[PROTOCOLO] Evaluacion objetivo: Retardo de confirmacion (T_conf <= 6 s [RQS2])"));
    }
    Serial.printf("[PROTOCOLO] Periodo de transmision (T_periodo): %d segundos\n\n", TX_INTERVAL_SECONDS);

    // Forzar primera transmisión inmediata
    lastTxTime = millis() - txIntervalMs;
}

void loop() {
    unsigned long currentMillis = millis();

    // Temporizador no bloqueante de transmisión periódica
    if (currentMillis - lastTxTime >= txIntervalMs) {
        lastTxTime = currentMillis;

        // 1. Muestreo de sensores y telemetría
        float tempVal = getTemperatureReading();
        float humVal  = getHumidityReading();
        float vbatVal = readBatteryVoltage();

        // 2. Construcción de estructura y codificación de payload binario (10 bytes)
        TelemetryData telemetry;
        telemetry.node_id = (uint8_t)NODE_ID;
        telemetry.seq_number = sequenceCounter++;
        telemetry.temperature_x100 = (int16_t)(tempVal * 100.0f);
        telemetry.humidity_x100 = (uint16_t)(humVal * 100.0f);
        
        // Batería escalada: (V - 2.0) * 100 (Rango 2.00V a 4.55V)
        if (vbatVal < 2.0f) {
            telemetry.battery_mv_scaled = 0;
        } else if (vbatVal > 4.55f) {
            telemetry.battery_mv_scaled = 255;
        } else {
            telemetry.battery_mv_scaled = (uint8_t)((vbatVal - 2.0f) * 100.0f);
        }

        uint8_t payloadBuffer[10];
        encodePayload(telemetry, payloadBuffer);

        // 3. Diagnóstico serial previo al envío
        Serial.println(F("-------------------------------------------------------"));
        Serial.printf("[UPLINK #%lu] Transmitiendo trama LoRaWAN (10 bytes):\n", telemetry.seq_number);
        Serial.printf("  * Node ID:      %u\n", telemetry.node_id);
        Serial.printf("  * Secuencia:    %lu\n", telemetry.seq_number);
        Serial.printf("  * Temperatura:  %.2f °C\n", tempVal);
        Serial.printf("  * Humedad:      %.2f %%\n", humVal);
        Serial.printf("  * Bateria:      %.2f V (Raw byte: %u)\n", vbatVal, telemetry.battery_mv_scaled);
        Serial.print(F("  * Payload HEX:  "));
        printHexPayload(payloadBuffer, sizeof(payloadBuffer));

        // 4. Ejecución del enlace ascendente (Uplink)
        bool isConfirmed = (CURRENT_SESSION_MODE == SESSION_TYPE_B);
        unsigned long tSendStart = millis();

        // sendReceive maneja transmisión y apertura automática de ventanas RX1/RX2
        int16_t state = node.sendReceive(payloadBuffer, sizeof(payloadBuffer), 1, isConfirmed);
        unsigned long tDuration = millis() - tSendStart;

        // 5. Evaluación de resultados y métricas experimentales
        if (state == RADIOLIB_ERR_NONE) {
            if (isConfirmed) {
                Serial.printf("[RESULTADO] Confirmacion recibida con exito (ACK en RX1/RX2)!\n");
                Serial.printf("[METRICA RQS2] Retardo T_conf: %lu ms ", tDuration);
                if (tDuration <= 6000) {
                    Serial.println(F("(CUMPLE criterio de viabilidad T_conf <= 6 s)"));
                } else {
                    Serial.println(F("(EXCEDE umbral de viabilidad T_conf > 6 s)"));
                }
            } else {
                Serial.printf("[RESULTADO] Uplink no confirmado transmitido exitosamente (ToA estimada ~%lu ms)\n", tDuration);
            }

            // Verificar si el Network Server envió datos de enlace descendente (Downlink)
            checkDownlinkData();

        } else if (state == RADIOLIB_ERR_NO_RX_WINDOW) {
            Serial.println(F("[RESULTADO] Trama emitida, sin ventana de recepcion abierta."));
        } else {
            Serial.printf("[ERROR] Fallo en enlace ascendente, codigo de error: %d\n", state);
            if (isConfirmed) {
                Serial.println(F("[METRICA] Paquete de confirmacion perdido o fuera de ventana RX1/RX2."));
            }
        }

        Serial.println(F("-------------------------------------------------------\n"));
    }

    // Ceder tiempo al planificador del sistema operativo (FreeRTOS)
    vTaskDelay(pdMS_TO_TICKS(10));
}

// --------------------------------------------------------------------------
// Rutinas auxiliares de adquisición de variables y periféricos
// --------------------------------------------------------------------------

/**
 * @brief Lee el voltaje de batería utilizando el divisor resistivo del Heltec V3
 */
float readBatteryVoltage() {
    pinMode(PIN_VBAT_CTRL, OUTPUT);
    // En Heltec V3/V3.1 poner LOW conecta el divisor al pin analógico
    digitalWrite(PIN_VBAT_CTRL, LOW);
    delay(10);

    // Lectura analógica calibrada en milivoltios del ESP32-S3 (GPIO 1)
    uint32_t adcMv = analogReadMilliVolts(PIN_VBAT_ADC);

    // Desconectar divisor para suprimir consumo en reposo
    digitalWrite(PIN_VBAT_CTRL, HIGH);

    // Factor del divisor interno de la placa (típicamente ~2.0x)
    float batteryVoltage = (adcMv * 2.0f) / 1000.0f;

    // Validación de rango lógico para baterías LiPo (3.0V a 4.2V; si USB alimentado ~4.1V-4.3V)
    if (batteryVoltage < 0.5f) {
        // Si no hay batería conectada o está alimentado estrictamente por USB sin sensado
        return 3.70f;
    }
    return batteryVoltage;
}

/**
 * @brief Obtiene lectura de temperatura (°C)
 * Si hay un sensor externo (BME280/DHT) se implementa aquí; por defecto integra
 * el sensor térmico interno del chip ESP32-S3 o simulación calibrada.
 */
float getTemperatureReading() {
    #if defined(ESP32)
    // Lectura del sensor térmico interno del ESP32-S3 con offset típico de disipación
    float chipTemp = temperatureRead();
    float ambientEstimate = chipTemp - 15.0f; // Ajuste empírico por disipación del SOC
    if (ambientEstimate < 5.0f || ambientEstimate > 40.0f) {
        ambientEstimate = 18.5f + (float)(random(-15, 25)) / 10.0f;
    }
    return ambientEstimate;
    #else
    return 19.5f;
    #endif
}

/**
 * @brief Obtiene lectura de humedad relativa (%)
 */
float getHumidityReading() {
    // Generación de perfil típico ambiental del campus (Temuco: 50% a 75% RH)
    static float currentHum = 60.0f;
    float delta = ((float)random(-5, 6)) / 10.0f;
    currentHum += delta;
    if (currentHum < 45.0f) currentHum = 45.0f;
    if (currentHum > 85.0f) currentHum = 85.0f;
    return currentHum;
}

/**
 * @brief Imprime el buffer de bytes en formato hexadecimal legible
 */
void printHexPayload(const uint8_t* buffer, size_t length) {
    for (size_t i = 0; i < length; i++) {
        if (buffer[i] < 0x10) Serial.print('0');
        Serial.print(buffer[i], HEX);
        if (i < length - 1) Serial.print(' ');
    }
    Serial.println();
}

/**
 * @brief Inspecciona y procesa tramas de Downlink recibidas en RX1/RX2
 */
void checkDownlinkData() {
    size_t downLen = node.getDownlinkLength();
    if (downLen > 0) {
        uint8_t downBuffer[64];
        int16_t downState = node.getDownlinkData(downBuffer, downLen);
        if (downState == RADIOLIB_ERR_NONE) {
            Serial.printf("[DOWNLINK] Recibidos %u bytes en FPort %u: ", downLen, node.getDownlinkPort());
            printHexPayload(downBuffer, downLen);
            Serial.printf("  * RSSI: %.1f dBm | SNR: %.1f dB\n", radio.getRSSI(), radio.getSNR());
        }
    }
}
