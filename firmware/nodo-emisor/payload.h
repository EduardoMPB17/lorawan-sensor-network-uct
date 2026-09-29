#ifndef PAYLOAD_H
#define PAYLOAD_H

#include <stdint.h>

struct TelemetryData {
    uint8_t  node_id;
    uint32_t seq_number;
    int16_t  temperature_x100;
    uint16_t humidity_x100;
    uint8_t  battery_mv_scaled;
};

inline void encodePayload(const TelemetryData& data, uint8_t* buffer) {
    // Byte 0: ID del nodo
    buffer[0] = data.node_id;

    // Bytes 1-4: Contador de secuencia (Big-Endian)
    buffer[1] = (uint8_t)((data.seq_number >> 24) & 0xFF);
    buffer[2] = (uint8_t)((data.seq_number >> 16) & 0xFF);
    buffer[3] = (uint8_t)((data.seq_number >> 8)  & 0xFF);
    buffer[4] = (uint8_t)(data.seq_number & 0xFF);

    // Bytes 5-6: Temperatura multiplicada por 100
    buffer[5] = (uint8_t)((data.temperature_x100 >> 8) & 0xFF);
    buffer[6] = (uint8_t)(data.temperature_x100 & 0xFF);

    // Bytes 7-8: Humedad multiplicada por 100
    buffer[7] = (uint8_t)((data.humidity_x100 >> 8) & 0xFF);
    buffer[8] = (uint8_t)(data.humidity_x100 & 0xFF);

    // Byte 9: Nivel de batería
    buffer[9] = data.battery_mv_scaled;
}

#endif // PAYLOAD_H