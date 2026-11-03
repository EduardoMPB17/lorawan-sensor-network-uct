import os

base = r'C:\Users\Administrador\Desktop\Tesis\lorawan-sensor-network-uct\chirpstack-docker'

# 1. mosquitto
p_mosq = os.path.join(base, 'configuration', 'mosquitto')
os.makedirs(p_mosq, exist_ok=True)
with open(os.path.join(p_mosq, 'mosquitto.conf'), 'w', encoding='utf-8') as f:
    f.write('listener 1883\nallow_anonymous true\n')

# 2. chirpstack-gateway-bridge
p_gw = os.path.join(base, 'configuration', 'chirpstack-gateway-bridge')
os.makedirs(p_gw, exist_ok=True)
with open(os.path.join(p_gw, 'chirpstack-gateway-bridge.toml'), 'w', encoding='utf-8') as f:
    f.write('''[general]
log_level=5

[backend.semtech_udp]
bind="0.0.0.0:1700"

[integration.mqtt]
server="tcp://mosquitto:1883"
event_topic_template="au915_2/gateway/{{ .GatewayID }}/event/{{ .EventType }}"
state_topic_template="au915_2/gateway/{{ .GatewayID }}/state/{{ .StateType }}"
command_topic_template="au915_2/gateway/{{ .GatewayID }}/command/{{ .CommandType }}"
''')

# 3. chirpstack.toml
p_cs = os.path.join(base, 'configuration', 'chirpstack')
os.makedirs(p_cs, exist_ok=True)
with open(os.path.join(p_cs, 'chirpstack.toml'), 'w', encoding='utf-8') as f:
    f.write('''[general]
log_level="info"

[postgresql]
dsn="postgres://root:root@postgres/chirpstack?sslmode=disable"

[redis]
servers=[
  "redis://redis:6379",
]

[network]
net_id="000000"
enabled_regions=[
  "au915_2",
]
''')

# 4. carpetas de datos
for d in ['postgres', 'redis', 'grafana', 'lorawan-devices']:
    os.makedirs(os.path.join(base, 'data', d), exist_ok=True)

print("Estructura de configuracion creada exitosamente!")
