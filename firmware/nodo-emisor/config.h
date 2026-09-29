#ifndef CONFIG_H
#define CONFIG_H

#include <Arduino.h>

/* ==========================================================================
 * TRABAJO DE TÍTULO - RED LORAWAN CAMPUS DR. LUIS RIVAS DEL CANTO (UCT)
 * Archivo de Configuración de Parámetros Técnicos y Credenciales
 * Hardware: Heltec WiFi LoRa 32 V3 (ESP32-S3 + Semtech SX1262)
 * ========================================================================== */

// --------------------------------------------------------------------------
// 1. REGLA DE SEGURIDAD DE HARDWARE (RT2)
// --------------------------------------------------------------------------
// ATENCIÓN: Conectar obligatoriamente la antena de 915 MHz al conector IPEX/U.FL
// o SMA antes de energizar la placa. Operar sin antena puede destruir
// permanentemente la etapa de potencia de RF del módulo SX1262.

// --------------------------------------------------------------------------
// 2. IDENTIFICACIÓN DEL NODO
// --------------------------------------------------------------------------
// Identificador numérico del nodo para distinguir el origen en el dashboard (RF4)
// Nodo 1: Exterior / Condición LOS (50 - 200 m)
// Nodo 2: Obstrucción parcial / Condición NLOS (100 - 350 m)
#define NODE_ID                     1

// --------------------------------------------------------------------------
// 3. CREDENCIALES OTAA (LoRaWAN 1.0.4 / 1.1)
// --------------------------------------------------------------------------
// Nota: Obtener estas credenciales desde la consola de ChirpStack v4.
// Los EUIs se configuran en formato Big-Endian (uint64_t).
// Las claves AES-128 se configuran como arreglos de 16 bytes.
#define LORAWAN_JOIN_EUI            0x0000000000000000ULL
#define LORAWAN_DEV_EUI             0x70B3D57ED0060001ULL

// Clave de aplicación (AppKey) - Reemplazar con la asignada en ChirpStack
static const uint8_t LORAWAN_APP_KEY[] = {
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

// Clave de red (NwkKey) - Para LoRaWAN 1.0.4 es idéntica a AppKey (o NULL en RadioLib)
static const uint8_t LORAWAN_NWK_KEY[] = {
    0x2B, 0x7E, 0x15, 0x16, 0x28, 0xAE, 0xD2, 0xA6,
    0xAB, 0xF7, 0x15, 0x88, 0x09, 0xCF, 0x4F, 0x3C
};

// --------------------------------------------------------------------------
// 4. PARÁMETROS REGIONALES Y DE RF (RT1 - SUBTEL Res. Ex. 1.985)
// --------------------------------------------------------------------------
// Banda AU915: 915 a 928 MHz.
// Sub-banda 2: Canales 8 al 15 (Uplink: 916.8 a 918.2 MHz; Downlink: 923.3 a 927.5 MHz)
#define AU915_SUBBAND               2

// Potencia máxima de transmisión: 14 dBm según normativa técnica chilena SUBTEL
#define LORA_TX_POWER_DBM           14

// Datarate LoRaWAN inicial para AU915:
// DR5 = SF7 / BW 125 kHz (Estándar para pruebas de referencia)
// DR3 = SF9 / BW 125 kHz (Para escenarios NLOS severos)
// DR0 = SF12 / BW 125 kHz (Máxima cobertura)
#define LORA_INITIAL_DATARATE       5

// --------------------------------------------------------------------------
// 5. MODOS DE SESIÓN EXPERIMENTAL (RF5 / RQS1 / RQS2)
// --------------------------------------------------------------------------
#define SESSION_TYPE_A              0   // No confirmada (Unconfirmed, NbTrans=1) -> Métrica: Packet Loss (PL <= 10%)
#define SESSION_TYPE_B              1   // Confirmada (Confirmed, con ACK) -> Métrica: Retardo T_conf (<= 6 s)

// Seleccionar el modo de sesión activo para la prueba de campo:
#define CURRENT_SESSION_MODE        SESSION_TYPE_A

// Intervalo de transmisión periódico: 60 segundos (cumple duty-cycle y plan de pruebas)
#define TX_INTERVAL_SECONDS         60

// --------------------------------------------------------------------------
// 6. MAPEO DE PINES HELTEC WIFI LORA 32 V3 (ESP32-S3 + SX1262)
// --------------------------------------------------------------------------
#define PIN_NSS                     8
#define PIN_RST                     12
#define PIN_BUSY                    13
#define PIN_DIO1                    14

// Control de alimentación de periféricos y bus VEXT (Activo en nivel bajo LOW)
#define PIN_VEXT                    36

// Medición de voltaje de batería (Divisor resistivo interno)
#define PIN_VBAT_ADC                1
#define PIN_VBAT_CTRL               37   // LOW en V3/V3.1 para habilitar lectura ADC

#endif // CONFIG_H
