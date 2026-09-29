/**
 * ==============================================================================
 * DASHBOARD WEB LORAWAN - CAMPUS DR. LUIS RIVAS DEL CANTO (UCT)
 * Lógica Cliente: Gestión de Estado, Gráficas Chart.js, MQTT y Simulación
 * ==============================================================================
 */

// Estado Global del Sistema
const appState = {
  mode: 'simulation', // 'simulation' o 'live'
  simulationTimer: null,
  totalFrames: 0,
  mqttClient: null,
  mqttConfig: {
    host: 'localhost',
    port: 9001,
    topic: 'uct/campus/lora/uplink/#'
  },
  nodes: {
    1: {
      id: 1,
      name: 'Nodo 1 (Exterior)',
      condition: 'LOS',
      seq: 0,
      temp: 18.5,
      hum: 62.0,
      vbat: 3.88,
      rssi: -66.0,
      snr: 9.5,
      lastSeen: null,
      status: 'online',
      nominalPeriodSec: 60
    },
    2: {
      id: 2,
      name: 'Nodo 2 (Obstrucción)',
      condition: 'NLOS',
      seq: 0,
      temp: 19.1,
      hum: 59.5,
      vbat: 3.75,
      rssi: -89.0, // Atenuación severa por muros (Modelo Log-Distance)
      snr: 2.5,
      lastSeen: null,
      status: 'online',
      nominalPeriodSec: 60
    }
  },
  history: [], // Historial de tramas recibidas (máximo 100)
  charts: {
    telemetry: null,
    rf: null
  }
};

// ------------------------------------------------------------------------------
// Inicialización al Cargar el DOM
// ------------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
  initCharts();
  initUIEventListeners();
  startSimulation();
  initAvailabilityChecker();
});

// ------------------------------------------------------------------------------
// Inicialización de Gráficas con Chart.js
// ------------------------------------------------------------------------------
function initCharts() {
  const ctxTelem = document.getElementById('chart-telemetry').getContext('2d');
  const ctxRf = document.getElementById('chart-rf').getContext('2d');

  // Configuración de estilo global para modo oscuro
  Chart.defaults.color = '#94A3B8';
  Chart.defaults.borderColor = 'rgba(255, 255, 255, 0.06)';
  Chart.defaults.font.family = "'Inter', sans-serif";

  // Gráfica 1: Temperatura y Humedad
  appState.charts.telemetry = new Chart(ctxTelem, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Temp Nodo 1 (LOS) [°C]',
          borderColor: '#06B6D4',
          backgroundColor: 'rgba(6, 182, 212, 0.1)',
          data: [],
          tension: 0.35,
          yAxisID: 'yTemp'
        },
        {
          label: 'Temp Nodo 2 (NLOS) [°C]',
          borderColor: '#F59E0B',
          backgroundColor: 'rgba(245, 158, 11, 0.1)',
          data: [],
          borderDash: [5, 5],
          tension: 0.35,
          yAxisID: 'yTemp'
        },
        {
          label: 'Hum Nodo 1 (LOS) [%]',
          borderColor: '#3B82F6',
          backgroundColor: 'transparent',
          data: [],
          tension: 0.35,
          yAxisID: 'yHum'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { grid: { display: false } },
        yTemp: {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'Temperatura (°C)' },
          min: 10,
          max: 35
        },
        yHum: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'Humedad (%)' },
          min: 30,
          max: 90,
          grid: { drawOnChartArea: false }
        }
      },
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12 } }
      }
    }
  });

  // Gráfica 2: Calidad RF (RSSI y SNR)
  appState.charts.rf = new Chart(ctxRf, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'RSSI N1 (LOS) [dBm]',
          borderColor: '#10B981',
          data: [],
          tension: 0.3,
          yAxisID: 'yRssi'
        },
        {
          label: 'RSSI N2 (NLOS) [dBm]',
          borderColor: '#EF4444',
          data: [],
          borderDash: [4, 4],
          tension: 0.3,
          yAxisID: 'yRssi'
        },
        {
          label: 'SNR N1 [dB]',
          borderColor: '#8B5CF6',
          data: [],
          tension: 0.3,
          yAxisID: 'ySnr'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        x: { grid: { display: false } },
        yRssi: {
          type: 'linear',
          position: 'left',
          title: { display: true, text: 'RSSI (dBm)' },
          min: -125,
          max: -40
        },
        ySnr: {
          type: 'linear',
          position: 'right',
          title: { display: true, text: 'SNR (dB)' },
          min: -15,
          max: 15,
          grid: { drawOnChartArea: false }
        }
      },
      plugins: {
        legend: { position: 'top', labels: { boxWidth: 12 } }
      }
    }
  });
}

// ------------------------------------------------------------------------------
// Ingesta y Procesamiento de Tramas de Telemetría
// ------------------------------------------------------------------------------
function processIncomingTelemetry(packet) {
  const nodeId = parseInt(packet.node_id || (packet.deviceInfo && packet.deviceInfo.nodeId) || 1, 10);
  const node = appState.nodes[nodeId];

  if (!node) {
    console.warn(`[WARN] Trama de nodo desconocido: ${nodeId}`);
    return;
  }

  const now = new Date();
  const timeStr = now.toLocaleTimeString();

  // Actualizar métricas del nodo
  node.seq = packet.sequence !== undefined ? packet.sequence : node.seq + 1;
  node.temp = parseFloat(packet.temperature !== undefined ? packet.temperature : node.temp);
  node.hum = parseFloat(packet.humidity !== undefined ? packet.humidity : node.hum);
  node.vbat = parseFloat(packet.battery_voltage !== undefined ? packet.battery_voltage : node.vbat);
  node.rssi = parseFloat(packet.rssi !== undefined ? packet.rssi : node.rssi);
  node.snr = parseFloat(packet.snr !== undefined ? packet.snr : node.snr);
  node.lastSeen = now;
  node.status = 'online';

  appState.totalFrames++;

  // 1. Actualizar Tarjeta del Nodo en el DOM
  updateNodeCardUI(nodeId);

  // 2. Actualizar KPIs Globales
  updateGlobalKPIs();

  // 3. Registrar en Historial y Tabla
  const record = {
    timestamp: now.toISOString(),
    timeLabel: timeStr,
    nodeId: node.id,
    nodeName: node.name,
    condition: node.condition,
    seq: node.seq,
    temp: node.temp.toFixed(2),
    hum: node.hum.toFixed(2),
    vbat: node.vbat.toFixed(2),
    rssi: node.rssi.toFixed(1),
    snr: node.snr.toFixed(1),
    status: 'Conforme'
  };

  appState.history.unshift(record);
  if (appState.history.length > 80) appState.history.pop();

  appendTableRow(record);

  // 4. Actualizar Gráficas
  updateChartsUI(timeStr);
}

// ------------------------------------------------------------------------------
// Actualización del DOM (Tarjetas de Nodos y KPIs)
// ------------------------------------------------------------------------------
function updateNodeCardUI(nodeId) {
  const node = appState.nodes[nodeId];
  const prefix = `node-${nodeId}`;

  // Valores numéricos
  document.getElementById(`${prefix}-temp`).textContent = node.temp.toFixed(1);
  document.getElementById(`${prefix}-hum`).textContent = node.hum.toFixed(1);
  document.getElementById(`${prefix}-batt`).textContent = node.vbat.toFixed(2);
  document.getElementById(`${prefix}-rssi`).textContent = `${node.rssi.toFixed(1)} dBm`;
  document.getElementById(`${prefix}-snr`).textContent = `${node.snr.toFixed(1)} dB`;
  document.getElementById(`${prefix}-seq`).textContent = `#${node.seq}`;

  // Porcentaje estimado de batería (LiPo 3.0V a 4.2V)
  let battPct = Math.round(((node.vbat - 3.2) / (4.2 - 3.2)) * 100);
  if (battPct > 100) battPct = 100;
  if (battPct < 0) battPct = 0;
  document.getElementById(`${prefix}-batt-pct`).textContent = `${battPct}%`;
  document.getElementById(`${prefix}-batt-bar`).style.width = `${battPct}%`;

  // Barras de progreso de temp y hum
  const tempPct = Math.min(Math.max(((node.temp - 5) / 35) * 100, 5), 100);
  document.getElementById(`${prefix}-temp-bar`).style.width = `${tempPct}%`;
  document.getElementById(`${prefix}-hum-bar`).style.width = `${node.hum}%`;

  // Calidad RF (RSSI)
  const rfBar = document.getElementById(`${prefix}-rf-bar`);
  const rfTag = document.getElementById(`${prefix}-rf-quality`);
  if (node.rssi >= -75) {
    rfTag.textContent = 'Excelente';
    rfBar.style.width = '90%';
  } else if (node.rssi >= -90) {
    rfTag.textContent = 'Aceptable';
    rfBar.style.width = '65%';
  } else if (node.rssi >= -110) {
    rfTag.textContent = 'Débil (NLOS)';
    rfBar.style.width = '35%';
  } else {
    rfTag.textContent = 'Crítico';
    rfBar.style.width = '15%';
  }

  // Delta de tiempo y estado
  document.getElementById(`${prefix}-last-seen`).textContent = 'Hace 0 s';
  const badge = document.getElementById(`${prefix}-status-badge`);
  badge.className = 'node-status-badge badge-online';
  badge.innerHTML = '<span class="dot"></span> Online';

  const deltaStatus = document.getElementById(`${prefix}-delta-status`);
  deltaStatus.className = 'delta-indicator';
  deltaStatus.textContent = 'Δt ≤ 3·T (Conforme)';
}

function updateGlobalKPIs() {
  document.getElementById('kpi-total-frames').textContent = appState.totalFrames.toLocaleString();
  document.getElementById('kpi-last-frame-time').textContent = `Última trama: ${new Date().toLocaleTimeString()}`;
  document.getElementById('records-count').textContent = `${appState.history.length} registros`;
}

// ------------------------------------------------------------------------------
// Inserción en Tabla de Telemetría
// ------------------------------------------------------------------------------
function appendTableRow(rec) {
  const tbody = document.getElementById('telemetry-tbody');
  
  // Remover fila vacía si existe
  const emptyRow = tbody.querySelector('.empty-row');
  if (emptyRow) emptyRow.remove();

  const tr = document.createElement('tr');
  const tagClass = rec.condition === 'LOS' ? 'tag-los' : 'tag-nlos';

  tr.innerHTML = `
    <td>${rec.timeLabel}</td>
    <td><strong>Nodo ${rec.nodeId}</strong></td>
    <td><span class="badge-tag-table ${tagClass}">${rec.condition}</span></td>
    <td>#${rec.seq}</td>
    <td>${rec.temp} °C</td>
    <td>${rec.hum} %</td>
    <td>${rec.vbat} V</td>
    <td>${rec.rssi} dBm</td>
    <td>${rec.snr} dB</td>
    <td><span style="color: var(--color-los); font-weight: 600;">✓ Recibido</span></td>
  `;

  tbody.insertBefore(tr, tbody.firstChild);

  // Mantener tamaño máximo de tabla
  while (tbody.children.length > 50) {
    tbody.removeChild(tbody.lastChild);
  }
}

// ------------------------------------------------------------------------------
// Actualización de Gráficas en Tiempo Real
// ------------------------------------------------------------------------------
function updateChartsUI(timeStr) {
  const telemChart = appState.charts.telemetry;
  const rfChart = appState.charts.rf;

  const n1 = appState.nodes[1];
  const n2 = appState.nodes[2];

  // Mantener ventana móvil de 15 puntos
  if (telemChart.data.labels.length > 15) {
    telemChart.data.labels.shift();
    telemChart.data.datasets[0].data.shift();
    telemChart.data.datasets[1].data.shift();
    telemChart.data.datasets[2].data.shift();

    rfChart.data.labels.shift();
    rfChart.data.datasets[0].data.shift();
    rfChart.data.datasets[1].data.shift();
    rfChart.data.datasets[2].data.shift();
  }

  telemChart.data.labels.push(timeStr);
  telemChart.data.datasets[0].data.push(n1.temp);
  telemChart.data.datasets[1].data.push(n2.temp);
  telemChart.data.datasets[2].data.push(n1.hum);
  telemChart.update('none');

  rfChart.data.labels.push(timeStr);
  rfChart.data.datasets[0].data.push(n1.rssi);
  rfChart.data.datasets[1].data.push(n2.rssi);
  rfChart.data.datasets[2].data.push(n1.snr);
  rfChart.update('none');
}

// ------------------------------------------------------------------------------
// Verificador Periódico de Disponibilidad (RQS3: Caída si Δt > 3·T_periodo)
// ------------------------------------------------------------------------------
function initAvailabilityChecker() {
  setInterval(() => {
    const now = new Date();
    let activeCount = 0;

    Object.values(appState.nodes).forEach(node => {
      const prefix = `node-${node.id}`;
      if (!node.lastSeen) return;

      const elapsedSec = Math.round((now - node.lastSeen) / 1000);
      document.getElementById(`${prefix}-last-seen`).textContent = `Hace ${elapsedSec} s`;

      // Regla RQS3: Si no hay tramas por más de 3 periodos nominales (180 s)
      const thresholdSec = node.nominalPeriodSec * 3;
      const deltaStatus = document.getElementById(`${prefix}-delta-status`);
      const badge = document.getElementById(`${prefix}-status-badge`);

      if (elapsedSec > thresholdSec) {
        node.status = 'offline';
        badge.className = 'node-status-badge badge-offline';
        badge.innerHTML = '<span class="dot"></span> Caído (Timeout)';
        deltaStatus.className = 'delta-indicator delta-alert';
        deltaStatus.textContent = `Δt = ${elapsedSec}s > 3·T (Caída RQS3)`;
      } else {
        activeCount++;
      }
    });

    document.getElementById('kpi-active-nodes').textContent = `${activeCount} / 2`;
    const availPct = (activeCount / 2) * 100;
    const availElem = document.getElementById('kpi-availability');
    availElem.textContent = `${availPct.toFixed(0)} %`;
    availElem.style.color = availPct >= 90 ? 'var(--color-los)' : 'var(--color-danger)';
  }, 2000);
}

// ------------------------------------------------------------------------------
// Motor de Simulación (Generador de Telemetría para Pruebas Inmediatas)
// ------------------------------------------------------------------------------
function startSimulation() {
  if (appState.simulationTimer) clearInterval(appState.simulationTimer);

  appState.mode = 'simulation';
  updateConnectionPill('sim');
  document.getElementById('btn-mode-text').textContent = 'Pausar Simulación';

  // Generar paquetes alternados entre Nodo 1 y Nodo 2 cada 4 segundos
  let toggle = true;
  appState.simulationTimer = setInterval(() => {
    const targetId = toggle ? 1 : 2;
    toggle = !toggle;

    const node = appState.nodes[targetId];

    // Simulación de fluctuación térmica y de humedad
    const deltaTemp = (Math.random() - 0.48) * 0.4;
    const deltaHum = (Math.random() - 0.5) * 0.6;
    const simulatedTemp = Math.round((node.temp + deltaTemp) * 100) / 100;
    const simulatedHum = Math.round(Math.min(Math.max(node.hum + deltaHum, 45), 85) * 100) / 100;

    // Simulación de propagación RF (Log-Distance con sombreado gaussiano X_sigma)
    // Nodo 1 (LOS): RSSI fuerte ~ -65 dBm, SNR alto ~ 9 dB
    // Nodo 2 (NLOS): RSSI atenuado ~ -88 dBm por obstáculos, SNR ~ 2.5 dB
    const baseRssi = targetId === 1 ? -66 : -89;
    const simulatedRssi = baseRssi + Math.round((Math.random() - 0.5) * 6);
    const simulatedSnr = targetId === 1 
      ? Math.round((9.0 + (Math.random() - 0.5) * 2) * 10) / 10
      : Math.round((2.5 + (Math.random() - 0.5) * 3) * 10) / 10;

    const packet = {
      node_id: targetId,
      sequence: node.seq + 1,
      temperature: simulatedTemp,
      humidity: simulatedHum,
      battery_voltage: (node.vbat - 0.0001).toFixed(2), // Consumo paulatino
      rssi: simulatedRssi,
      snr: simulatedSnr
    };

    processIncomingTelemetry(packet);
  }, 4000);
}

function stopSimulation() {
  if (appState.simulationTimer) {
    clearInterval(appState.simulationTimer);
    appState.simulationTimer = null;
  }
  document.getElementById('btn-mode-text').textContent = 'Reanudar Simulación';
}

// ------------------------------------------------------------------------------
// Cliente MQTT sobre WebSockets (Paho MQTT)
// ------------------------------------------------------------------------------
function connectMQTT() {
  stopSimulation();
  appState.mode = 'live';

  const host = appState.mqttConfig.host;
  const port = parseInt(appState.mqttConfig.port, 10);
  const topic = appState.mqttConfig.topic;

  updateConnectionPill('connecting');

  const clientId = `uct_web_dash_${Math.random().toString(16).substr(2, 8)}`;
  const client = new Paho.MQTT.Client(host, port, clientId);

  client.onConnectionLost = (responseObject) => {
    console.warn('[MQTT] Conexión perdida:', responseObject.errorMessage);
    updateConnectionPill('disconnected');
  };

  client.onMessageArrived = (message) => {
    try {
      const payload = JSON.parse(message.payloadString);
      processIncomingTelemetry(payload);
    } catch (e) {
      console.error('[MQTT] Error decodificando payload JSON:', e);
    }
  };

  client.connect({
    onSuccess: () => {
      console.log('[MQTT] Conexión WebSocket establecida con éxito.');
      client.subscribe(topic);
      updateConnectionPill('live');
      appState.mqttClient = client;
    },
    onFailure: (err) => {
      console.error('[MQTT] Falló conexión WebSocket:', err);
      alert(`No se pudo conectar a ws://${host}:${port}. Verifique que el broker MQTT tenga WebSockets habilitados.`);
      updateConnectionPill('disconnected');
      // Reanudar simulación como fallback
      startSimulation();
    }
  });
}

function updateConnectionPill(status) {
  const dot = document.getElementById('status-dot');
  const label = document.getElementById('status-label');

  if (status === 'live') {
    dot.className = 'status-dot pulsating';
    dot.style.backgroundColor = 'var(--color-los)';
    label.textContent = `MQTT en Vivo (${appState.mqttConfig.host}:${appState.mqttConfig.port})`;
  } else if (status === 'sim') {
    dot.className = 'status-dot pulsating';
    dot.style.backgroundColor = 'var(--primary)';
    label.textContent = 'Modo Simulación Activo';
  } else if (status === 'connecting') {
    dot.className = 'status-dot pulsating';
    dot.style.backgroundColor = 'var(--color-nlos)';
    label.textContent = 'Conectando a MQTT...';
  } else {
    dot.className = 'status-dot offline';
    label.textContent = 'MQTT Desconectado';
  }
}

// ------------------------------------------------------------------------------
// Exportación a CSV
// ------------------------------------------------------------------------------
function exportHistoryToCSV() {
  if (appState.history.length === 0) {
    alert('No hay registros de telemetría para exportar.');
    return;
  }

  const headers = ['Timestamp_ISO', 'Hora_Local', 'Nodo_ID', 'Nombre', 'Condicion', 'Secuencia', 'Temperatura_C', 'Humedad_Pct', 'Bateria_V', 'RSSI_dBm', 'SNR_dB', 'Estado'];
  const rows = appState.history.map(r => [
    r.timestamp,
    r.timeLabel,
    r.nodeId,
    `"${r.nodeName}"`,
    r.condition,
    r.seq,
    r.temp,
    r.hum,
    r.vbat,
    r.rssi,
    r.snr,
    r.status
  ]);

  const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
  const encodedUri = encodeURI(csvContent);
  const link = document.createElement('a');
  link.setAttribute('href', encodedUri);
  link.setAttribute('download', `telemetria_lorawan_uct_${new Date().toISOString().slice(0, 10)}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// ------------------------------------------------------------------------------
// Manejo de Eventos UI y Modales
// ------------------------------------------------------------------------------
function initUIEventListeners() {
  // Alternar simulación
  document.getElementById('btn-toggle-mode').addEventListener('click', () => {
    if (appState.simulationTimer) {
      stopSimulation();
    } else {
      startSimulation();
    }
  });

  // Exportar CSV
  document.getElementById('btn-export-csv').addEventListener('click', exportHistoryToCSV);

  // Modal de configuración
  const modal = document.getElementById('settings-modal');
  document.getElementById('btn-open-settings').addEventListener('click', () => modal.showModal());
  document.getElementById('btn-close-modal').addEventListener('click', () => modal.close());
  document.getElementById('btn-cancel-settings').addEventListener('click', () => modal.close());

  // Guardar configuración y conectar
  document.getElementById('form-mqtt-settings').addEventListener('submit', (e) => {
    e.preventDefault();
    appState.mqttConfig.host = document.getElementById('input-mqtt-host').value.trim();
    appState.mqttConfig.port = document.getElementById('input-mqtt-port').value.trim();
    appState.mqttConfig.topic = document.getElementById('input-mqtt-topic').value.trim();
    modal.close();
    connectMQTT();
  });
}
