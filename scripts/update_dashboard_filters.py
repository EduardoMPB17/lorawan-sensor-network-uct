# -*- coding: utf-8 -*-
"""
Script para actualizar dashboard_server.py con el nuevo sistema de filtros avanzados
(Fechas, Horarios, Franjas de la Tesis, Nodos y Vista Previa en Vivo).
"""

import re

with open("dashboard_server.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Actualizar imports
if "from urllib.parse import urlparse, parse_qs" not in content:
    content = content.replace(
        "from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer",
        "from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer\nfrom urllib.parse import urlparse, parse_qs"
    )

# 2. Agregar helper build_telemetry_query antes de HTML_PAGE
helper_code = '''
def build_telemetry_query(params):
    query = 'SELECT id, timestamp, device_name, dev_eui, temperature, humidity, battery_mv, battery_pct, packet_seq, status_flags, rssi, snr, f_cnt FROM telemetry WHERE 1=1'
    sql_params = []
    
    node = params.get('node', [''])[0]
    if node and node != 'ALL':
        query += ' AND (device_name = ? OR dev_eui LIKE ?)'
        sql_params.extend([node, f"%{node}%"])
        
    start_date = params.get('start_date', [''])[0]
    if start_date:
        query += ' AND date(timestamp) >= ?'
        sql_params.append(start_date)
        
    end_date = params.get('end_date', [''])[0]
    if end_date:
        query += ' AND date(timestamp) <= ?'
        sql_params.append(end_date)
        
    start_time = params.get('start_time', [''])[0]
    if start_time:
        if len(start_time) == 5: start_time += ":00"
        query += ' AND time(timestamp) >= ?'
        sql_params.append(start_time)
        
    end_time = params.get('end_time', [''])[0]
    if end_time:
        if len(end_time) == 5: end_time += ":59"
        query += ' AND time(timestamp) <= ?'
        sql_params.append(end_time)
        
    slot = params.get('slot', [''])[0]
    if slot == 'manana':
        query += " AND time(timestamp) BETWEEN '08:00:00' AND '11:59:59'"
    elif slot == 'mediodia':
        query += " AND time(timestamp) BETWEEN '12:00:00' AND '14:59:59'"
    elif slot == 'tarde':
        query += " AND time(timestamp) BETWEEN '15:00:00' AND '18:59:59'"
    elif slot == 'noche':
        query += " AND (time(timestamp) >= '19:00:00' OR time(timestamp) <= '07:59:59')"

    since_id = params.get('since_id', [''])[0]
    if since_id:
        try:
            query += ' AND id >= ?'
            sql_params.append(int(since_id))
        except: pass
        
    return query, sql_params

HTML_PAGE = """<!DOCTYPE html>'''

if "def build_telemetry_query(params):" not in content:
    content = content.replace('HTML_PAGE = """<!DOCTYPE html>', helper_code)

# 3. Agregar estilos del Modal antes de </style>
modal_css = '''
    /* MODAL DE EXPORTACIÓN AVANZADA */
    .modal-backdrop {
      position: fixed; top: 0; left: 0; width: 100%; height: 100%;
      background: rgba(11, 15, 25, 0.85); backdrop-filter: blur(8px);
      display: none; align-items: center; justify-content: center;
      z-index: 9999; padding: 20px;
    }
    .modal-backdrop.active { display: flex; }
    .modal-box {
      background: #111827; border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 18px; width: 100%; max-width: 650px; padding: 26px;
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.7); animation: modalAnim 0.2s ease-out;
      max-height: 90vh; overflow-y: auto;
    }
    @keyframes modalAnim { from { opacity: 0; transform: scale(0.96) translateY(10px); } to { opacity: 1; transform: scale(1) translateY(0); } }
    .modal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 14px; }
    .modal-header h2 { font-size: 20px; font-weight: 800; display: flex; align-items: center; gap: 10px; color: var(--text); }
    .modal-close { background: transparent; border: none; font-size: 24px; color: var(--text-muted); cursor: pointer; transition: color 0.2s; line-height: 1; }
    .modal-close:hover { color: var(--text); }
    .filter-section { margin-bottom: 18px; }
    .filter-section-title { font-size: 12px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; color: var(--cyan); margin-bottom: 8px; }
    .pill-group { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 10px; }
    .pill-btn {
      background: rgba(30, 41, 59, 0.8); border: 1px solid var(--border);
      color: var(--text-muted); padding: 6px 12px; border-radius: 7px;
      font-size: 12.5px; font-weight: 600; cursor: pointer; transition: all 0.2s;
    }
    .pill-btn:hover { background: rgba(51, 65, 85, 0.9); color: var(--text); }
    .pill-btn.active { background: rgba(56, 189, 248, 0.2); border-color: var(--cyan); color: var(--cyan); }
    .input-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
    .input-field-group label { display: block; font-size: 11.5px; color: var(--text-muted); margin-bottom: 4px; }
    .modal-input {
      width: 100%; background: rgba(15, 23, 42, 0.8); border: 1px solid var(--border);
      border-radius: 8px; padding: 8px 12px; color: var(--text); font-size: 13px; outline: none;
    }
    .modal-input:focus { border-color: var(--cyan); }
    .export-preview-box {
      background: rgba(15, 23, 42, 0.6); border: 1px solid var(--border);
      border-radius: 12px; padding: 14px 18px; margin: 18px 0;
      display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap;
    }
    .preview-count { font-size: 14px; font-weight: 700; color: var(--emerald); display: flex; align-items: center; gap: 6px; }
    .preview-count.empty { color: var(--amber); }
    .modal-footer { display: flex; justify-content: flex-end; gap: 10px; margin-top: 22px; border-top: 1px solid var(--border); padding-top: 16px; flex-wrap: wrap; }
  </style>
'''

if "/* MODAL DE EXPORTACIÓN AVANZADA */" not in content:
    content = content.replace("  </style>", modal_css)

# 4. Modificar el botón del header
header_btn_old = '<a href="/api/export-csv" class="btn btn-primary" download="telemetria_lorawan_uct.csv">📥 Exportar Todo</a>'
header_btn_new = '<button class="btn btn-primary" onclick="openExportModal()">📥 Exportar / Filtrar CSV</button>'
content = content.replace(header_btn_old, header_btn_new)

# 5. Agregar el marcado del Modal antes de </body>
modal_html = '''
  <!-- MODAL DE EXPORTACIÓN AVANZADA (FILTRO POR DÍAS, HORAS Y NODOS) -->
  <div class="modal-backdrop" id="modal-export" onclick="if(event.target===this) closeExportModal()">
    <div class="modal-box">
      <div class="modal-header">
        <div>
          <h2><span>📊</span> Exportación Avanzada de Telemetría</h2>
          <div style="font-size: 12.5px; color: var(--text-muted); margin-top: 4px;">Filtra y descarga conjuntos de datos ordenados para la memoria de título (Metodología PPDIOO).</div>
        </div>
        <button class="modal-close" onclick="closeExportModal()">&times;</button>
      </div>

      <!-- 1. FILTRO DE NODO -->
      <div class="filter-section">
        <div class="filter-section-title">1. Dispositivo / Nodo</div>
        <div class="pill-group" id="group-exp-node">
          <button class="pill-btn active" data-node="ALL" onclick="setExpNode('ALL')">🌐 Todos los Nodos</button>
          <button class="pill-btn" data-node="Heltec-V3-Nodo1" onclick="setExpNode('Heltec-V3-Nodo1')">📡 Nodo 1 (LOS)</button>
          <button class="pill-btn" data-node="Heltec-V3-Nodo2" onclick="setExpNode('Heltec-V3-Nodo2')">🏢 Nodo 2 (NLOS)</button>
        </div>
      </div>

      <!-- 2. FILTRO DE FECHAS (DÍAS) -->
      <div class="filter-section">
        <div class="filter-section-title">2. Rango de Fechas (Días de Prueba)</div>
        <div class="pill-group" id="group-exp-date">
          <button class="pill-btn active" data-date="all" onclick="setExpDatePreset('all')">🌐 Todo el Historial</button>
          <button class="pill-btn" data-date="today" onclick="setExpDatePreset('today')">📅 Hoy</button>
          <button class="pill-btn" data-date="yesterday" onclick="setExpDatePreset('yesterday')">⏮️ Ayer</button>
          <button class="pill-btn" data-date="last3" onclick="setExpDatePreset('last3')">🗓️ Últimos 3 Días</button>
        </div>
        <div class="input-row">
          <div class="input-field-group">
            <label>Fecha Desde:</label>
            <input type="date" id="exp-start-date" class="modal-input" onchange="onExpDateChange()">
          </div>
          <div class="input-field-group">
            <label>Fecha Hasta:</label>
            <input type="date" id="exp-end-date" class="modal-input" onchange="onExpDateChange()">
          </div>
        </div>
      </div>

      <!-- 3. FILTRO DE HORAS (FRANJAS HORARIAS DE LA TESIS) -->
      <div class="filter-section">
        <div class="filter-section-title">3. Franjas Horarias (Criterio de Evaluación Tesis)</div>
        <div class="pill-group" id="group-exp-slot">
          <button class="pill-btn active" data-slot="all" onclick="setExpSlotPreset('all')">⏰ Todo el Día (00:00 - 23:59)</button>
          <button class="pill-btn" data-slot="manana" onclick="setExpSlotPreset('manana')">🌅 Mañana (08:00 - 12:00)</button>
          <button class="pill-btn" data-slot="mediodia" onclick="setExpSlotPreset('mediodia')">☀️ Mediodía (12:00 - 15:00)</button>
          <button class="pill-btn" data-slot="tarde" onclick="setExpSlotPreset('tarde')">🌇 Tarde (15:00 - 19:00)</button>
          <button class="pill-btn" data-slot="noche" onclick="setExpSlotPreset('noche')">🌙 Noche (19:00 - 23:59)</button>
        </div>
        <div class="input-row">
          <div class="input-field-group">
            <label>Hora Inicio Manual (opcional):</label>
            <input type="time" id="exp-start-time" class="modal-input" onchange="onExpTimeChange()">
          </div>
          <div class="input-field-group">
            <label>Hora Fin Manual (opcional):</label>
            <input type="time" id="exp-end-time" class="modal-input" onchange="onExpTimeChange()">
          </div>
        </div>
      </div>

      <!-- 4. VISTA PREVIA Y NOMBRE DE ARCHIVO -->
      <div class="export-preview-box">
        <div>
          <div style="font-size: 11px; text-transform: uppercase; color: var(--text-muted); font-weight: 700;">Tramas Coincidentes:</div>
          <div class="preview-count" id="exp-preview-count">🔍 Calculando tramas...</div>
        </div>
        <div style="flex: 1; min-width: 220px;">
          <label style="font-size: 11px; color: var(--text-muted); font-weight: 700; display: block; margin-bottom: 3px;">Nombre de Archivo CSV:</label>
          <input type="text" id="exp-filename" class="modal-input" style="font-family: monospace; font-size: 12px;">
        </div>
      </div>

      <!-- FOOTER ACCIONES -->
      <div class="modal-footer">
        <button class="btn" onclick="closeExportModal()">Cancelar</button>
        <a href="/api/export-csv" class="btn" download="telemetria_completa.csv" style="color: var(--text-muted);">📥 Descargar Todo (Sin Filtro)</a>
        <button class="btn btn-primary" id="btn-do-export" onclick="executeFilteredExport()">📥 Descargar CSV Filtrado</button>
      </div>
    </div>
  </div>
'''

if 'id="modal-export"' not in content:
    content = content.replace("</body>", modal_html + "\n</body>")

# 6. Agregar funciones JavaScript del modal antes de </script>
modal_js = '''
    // ==========================================
    // LÓGICA DE EXPORTACIÓN AVANZADA
    // ==========================================
    let expCurrentNode = 'ALL';
    let expCurrentSlot = 'all';
    let expDebounceTimer = null;

    function openExportModal() {
      // Sincronizar nodo con el filtro actual del dashboard
      expCurrentNode = selectedNode || 'ALL';
      setExpNode(expCurrentNode);
      document.getElementById('modal-export').classList.add('active');
      triggerExportPreview();
    }

    function closeExportModal() {
      document.getElementById('modal-export').classList.remove('active');
    }

    function setExpNode(node) {
      expCurrentNode = node;
      document.querySelectorAll('#group-exp-node .pill-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-node') === node);
      });
      triggerExportPreview();
    }

    function setExpDatePreset(preset) {
      document.querySelectorAll('#group-exp-date .pill-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-date') === preset);
      });
      
      const inStart = document.getElementById('exp-start-date');
      const inEnd = document.getElementById('exp-end-date');
      const now = new Date();
      const fmt = d => d.toISOString().split('T')[0];

      if (preset === 'today') {
        inStart.value = fmt(now);
        inEnd.value = fmt(now);
      } else if (preset === 'yesterday') {
        const y = new Date(now);
        y.setDate(y.getDate() - 1);
        inStart.value = fmt(y);
        inEnd.value = fmt(y);
      } else if (preset === 'last3') {
        const past = new Date(now);
        past.setDate(past.getDate() - 3);
        inStart.value = fmt(past);
        inEnd.value = fmt(now);
      } else {
        inStart.value = '';
        inEnd.value = '';
      }
      triggerExportPreview();
    }

    function onExpDateChange() {
      document.querySelectorAll('#group-exp-date .pill-btn').forEach(b => b.classList.remove('active'));
      triggerExportPreview();
    }

    function setExpSlotPreset(slot) {
      expCurrentSlot = slot;
      document.querySelectorAll('#group-exp-slot .pill-btn').forEach(b => {
        b.classList.toggle('active', b.getAttribute('data-slot') === slot);
      });

      const inStart = document.getElementById('exp-start-time');
      const inEnd = document.getElementById('exp-end-time');

      if (slot === 'manana') {
        inStart.value = '08:00'; inEnd.value = '12:00';
      } else if (slot === 'mediodia') {
        inStart.value = '12:00'; inEnd.value = '15:00';
      } else if (slot === 'tarde') {
        inStart.value = '15:00'; inEnd.value = '19:00';
      } else if (slot === 'noche') {
        inStart.value = '19:00'; inEnd.value = '23:59';
      } else {
        inStart.value = ''; inEnd.value = '';
      }
      triggerExportPreview();
    }

    function onExpTimeChange() {
      expCurrentSlot = 'custom';
      document.querySelectorAll('#group-exp-slot .pill-btn').forEach(b => b.classList.remove('active'));
      triggerExportPreview();
    }

    function getExportQueryString() {
      const sDate = document.getElementById('exp-start-date').value;
      const eDate = document.getElementById('exp-end-date').value;
      const sTime = document.getElementById('exp-start-time').value;
      const eTime = document.getElementById('exp-end-time').value;

      const p = new URLSearchParams();
      if (expCurrentNode && expCurrentNode !== 'ALL') p.append('node', expCurrentNode);
      if (sDate) p.append('start_date', sDate);
      if (eDate) p.append('end_date', eDate);
      if (sTime) p.append('start_time', sTime);
      if (eTime) p.append('end_time', eTime);
      if (expCurrentSlot && expCurrentSlot !== 'all' && expCurrentSlot !== 'custom') {
        p.append('slot', expCurrentSlot);
      }
      return p;
    }

    function triggerExportPreview() {
      clearTimeout(expDebounceTimer);
      expDebounceTimer = setTimeout(async () => {
        const p = getExportQueryString();
        const lbl = document.getElementById('exp-preview-count');
        const btn = document.getElementById('btn-do-export');
        const inFilename = document.getElementById('exp-filename');

        // Sugerir nombre de archivo
        let nodePart = expCurrentNode === 'ALL' ? 'TodosNodos' : (expCurrentNode.includes('Nodo1') ? 'Nodo1_LOS' : 'Nodo2_NLOS');
        let datePart = document.getElementById('exp-start-date').value || 'Historial';
        let slotPart = expCurrentSlot === 'all' ? 'Completo' : expCurrentSlot;
        inFilename.value = `lorawan_${nodePart}_${datePart}_${slotPart}.csv`;

        lbl.innerHTML = '⏳ Verificando registros...';
        try {
          const res = await fetch(`/api/export-count?${p.toString()}&_=${Date.now()}`);
          const json = await res.json();
          const count = json.count || 0;
          if (count > 0) {
            lbl.className = 'preview-count';
            lbl.innerHTML = `✅ <strong>${count}</strong> tramas encontradas`;
            btn.disabled = false;
            btn.innerHTML = `📥 Descargar CSV (${count} tramas)`;
          } else {
            lbl.className = 'preview-count empty';
            lbl.innerHTML = `⚠️ 0 tramas para este filtro`;
            btn.disabled = true;
            btn.innerHTML = `📥 Sin datos para descargar`;
          }
        } catch (e) {
          lbl.innerHTML = 'Error al consultar base de datos';
        }
      }, 150);
    }

    function executeFilteredExport() {
      const p = getExportQueryString();
      const fn = document.getElementById('exp-filename').value.trim() || 'telemetria_lorawan_filtrada.csv';
      p.append('filename', fn);
      window.location.href = `/api/export-csv?${p.toString()}`;
    }
'''

if "function openExportModal()" not in content:
    content = content.replace("  </script>", modal_js + "\n  </script>")

# 7. Actualizar endpoints en DashboardHandler (do_GET)
endpoint_code = '''        elif self.path.startswith('/api/export-count'):
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            query, sql_params = build_telemetry_query(params)
            count_query = 'SELECT COUNT(*) FROM (' + query + ')'
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute(count_query, sql_params)
            count = c.fetchone()[0]
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.end_headers()
            self.wfile.write(json.dumps({'count': count}).encode('utf-8'))

        elif self.path.startswith('/api/export-csv'):
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            query, sql_params = build_telemetry_query(params)
            query += ' ORDER BY id ASC'
            
            filename = params.get('filename', ['telemetria_lorawan_campus_uct.csv'])[0]
            if not filename.endswith('.csv'): filename += '.csv'
            
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute(query, sql_params)
            rows = c.fetchall()
            conn.close()

            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Fecha y Hora', 'Dispositivo', 'DevEUI', 'Temperatura (°C)', 'Humedad (%)', 'Batería (mV)', 'Batería (%)', 'Secuencia', 'Status Flags', 'RSSI (dBm)', 'SNR (dB)', 'FCnt'])
            for r in rows:
                writer.writerow(list(r))

            csv_bytes = output.getvalue().encode('utf-8-sig')
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
            self.end_headers()
            self.wfile.write(csv_bytes)
'''

# Reemplazar el bloque elif self.path.startswith('/api/export-csv')
pattern = r"        elif self\.path\.startswith\('/api/export-csv'\):[\s\S]*?self\.wfile\.write\(csv_bytes\)"
content = re.sub(pattern, endpoint_code, content)

with open("dashboard_server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("dashboard_server.py actualizado con éxito!")
