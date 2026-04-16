#!/usr/bin/env python3
"""ClinicalMarket Dashboard v8 — Canal RETAIL
Para el equipo comercial: campañas, visitas, ventas, oportunidades.
Todos los datos se leen desde archivos JSON en /data.
Flujo mensual: actualizar los JSONs → push → GitHub Actions regenera el dashboard."""

import json, os, textwrap
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATHS = [
    os.path.join(SCRIPT_DIR, '..', 'data'),
    os.path.join(SCRIPT_DIR, 'data'),
]

def find_data():
    for p in DATA_PATHS:
        if os.path.isfile(os.path.join(p, 'clientes_data.json')):
            return p
    raise FileNotFoundError("No se encontró data dir con clientes_data.json")

DATA_DIR = find_data()

# ============================================================
# LOAD ALL DATA FROM JSON FILES
# ============================================================
def load_json(filename):
    path = os.path.join(DATA_DIR, filename)
    with open(path, encoding='utf-8') as f:
        return json.load(f)

clientes = load_json('clientes_data.json')
comp = load_json('comparativo.json')
skus = load_json('sku_data.json')
meses = load_json('campanas_mensuales.json')
campanas_digitales = load_json('campanas_digitales.json')
top_productos_digital = load_json('productos_digital.json')

# GA4 data
ga4 = load_json('ga4_visitas.json')
visitas_fuente = ga4['visitas_fuente']
visitas_mensuales = ga4['visitas_mensuales']

# Mailing — read from mailing.json, use latest entry
mailing_list = load_json('mailing.json')
_last_mail = mailing_list[-1] if mailing_list else {}
# Find sesiones_email from visitas_fuente (Email / MailUp row)
_sesiones_email = next((f['sesiones'] for f in visitas_fuente if 'email' in f['fuente'].lower() or 'mailup' in f['fuente'].lower()), 0)
mailing = {
    "ultima_campana": _last_mail.get("nombre", "—"),
    "enviados": _last_mail.get("enviados", 0),
    "aperturas": _last_mail.get("aperturas", 0),
    "tasa_apertura": _last_mail.get("tasa_apertura", 0),
    "clics": _last_mail.get("clics", 0),
    "tasa_clic": _last_mail.get("tasa_clic", 0),
    "sesiones_email": _sesiones_email,
}

# Build timestamp (Spanish month names)
_MESES_ES = {1:'Enero',2:'Febrero',3:'Marzo',4:'Abril',5:'Mayo',6:'Junio',
             7:'Julio',8:'Agosto',9:'Septiembre',10:'Octubre',11:'Noviembre',12:'Diciembre'}
_now = datetime.now()
GENERATED_DATE = f"{_now.day} {_MESES_ES[_now.month]} {_now.year}"

# ============================================================
# Derived metrics
# ============================================================
res = comp['resumen']
venta_25 = int(float(res['venta_mar25']))
venta_26 = int(float(res['venta_mar26']))
crec_venta = round((venta_26 - venta_25) / venta_25 * 100, 1) if venta_25 else 0
unid_25 = int(float(res['unid_mar25']))
unid_26 = int(float(res['unid_mar26']))
crec_unid = round((unid_26 - unid_25) / unid_25 * 100, 1) if unid_25 else 0
margen_26 = round(float(res['pct_margen_26']) * 100, 1)

total_ventas_6m = sum(m['ventas'] for m in meses)
total_unid_6m = sum(m['unidades'] for m in meses)
best_month = max(meses, key=lambda x: x['ventas'])

# Campañas sorted by venta_26
camp_crecimiento = [c for c in comp['campanas'] if c['venta_26'] > 0 and c['nombre'] != 'SIN CAMPAÑA']
camp_crecimiento.sort(key=lambda x: x['venta_26'], reverse=True)

# Digital totals
total_visitas_catalogo = sum(c['visitas_catalogo'] for c in campanas_digitales)
total_clics_productos = sum(c['clics_productos'] for c in campanas_digitales)
total_compras_digital = sum(c['compras_post_clic'] for c in campanas_digitales)
total_venta_digital = sum(c['venta_atribuida'] for c in campanas_digitales)
total_visitas_b2b_mar = visitas_mensuales[-1]['visitas_b2b']

# Mailing derived metrics
avg_tasa_apertura = round(sum(m['tasa_apertura'] for m in mailing_list) / len(mailing_list), 1) if mailing_list else 0
avg_tasa_clic = round(sum(m['tasa_clic'] for m in mailing_list) / len(mailing_list), 1) if mailing_list else 0
total_enviados = sum(m['enviados'] for m in mailing_list)

# Pre-computed conditional values (for f-string compatibility)
arrow_venta = '▲' if crec_venta > 0 else '▼'
color_venta = 'var(--success)' if crec_venta > 0 else 'var(--danger)'
kpi_class_venta = 'kpi-green' if crec_venta > 0 else 'kpi-red'
arrow_unid = '▲' if crec_unid > 0 else '▼'
kpi_class_unid = 'kpi-red' if crec_unid < 0 else 'kpi-green'

# ============================================================
# HTML GENERATION
# ============================================================

def fmt_clp(n):
    """Format CLP currency with dots as thousands separator (Chilean format)."""
    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:,.2f}MM".replace(",", ".")
    elif n >= 1_000_000:
        return f"${n/1_000_000:,.1f}M".replace(",", ".")
    else:
        return f"${n:,.0f}".replace(",", ".")

def fmt_pct(n):
    return f"{n:+.1f}%" if n else "—"

# ---- Pre-build table rows ----

# Campaign comparison rows
camp_rows_html = ""
for c in comp['campanas']:
    if c['nombre'] == 'SIN CAMPAÑA':
        continue
    delta = c['venta_26'] - c['venta_25']
    arrow = "▲" if delta > 0 else "▼" if delta < 0 else "→"
    color = "#27ae60" if delta > 0 else "#e74c3c" if delta < 0 else "#95a5a6"
    pct_crec = round(delta / c['venta_25'] * 100, 1) if c['venta_25'] else 0
    camp_rows_html += f"""<tr>
        <td><strong>{c['nombre']}</strong></td>
        <td>{c['skus']}</td>
        <td style="text-align:right">{fmt_clp(c['venta_25'])}</td>
        <td style="text-align:right;font-weight:600">{fmt_clp(c['venta_26'])}</td>
        <td style="color:{color};font-weight:700">{arrow} {fmt_clp(abs(delta))} ({pct_crec:+.0f}%)</td>
        <td><span style="color:#27ae60">+{c['grew']} crecieron</span> · <span style="color:#0DA7EE">{c['new']} nuevos</span> · <span style="color:#e74c3c">{c['dropped']} cayeron</span></td>
    </tr>"""

# Clientes top rows
cli_rows = ""
for i, c in enumerate(clientes['top50'][:30]):
    pct = round(c['venta_total'] / clientes['total_venta'] * 100, 1)
    cli_rows += f"""<tr>
        <td>{i+1}</td>
        <td>{c['nombre']}</td>
        <td>{c['vendedor']}</td>
        <td style="text-align:right;font-weight:600">{fmt_clp(c['venta_total'])}</td>
        <td>{pct}%</td>
    </tr>"""

# Top SKUs comparativo
sku_comp_rows = ""
for s in comp['top_skus'][:20]:
    arrow = "▲" if s['delta'] > 0 else "▼" if s['delta'] < 0 else "→"
    color = "#27ae60" if s['delta'] > 0 else "#e74c3c" if s['delta'] < 0 else "#95a5a6"
    crec = f"{s['crec_pct']}%" if s['crec_pct'] else "NUEVO"
    sku_comp_rows += f"""<tr>
        <td>{s['sku']}</td>
        <td>{s['desc'][:45]}</td>
        <td><span class="badge">{s['campana']}</span></td>
        <td style="text-align:right">{fmt_clp(s['venta_25'])}</td>
        <td style="text-align:right;font-weight:600">{fmt_clp(s['venta_26'])}</td>
        <td style="color:{color};font-weight:700">{arrow} {crec}</td>
    </tr>"""

# Invierno rows
inv_rows = ""
for s in comp['invierno_2026'][:15]:
    crec = f"{s['crec_feb_mar']}%" if s['crec_feb_mar'] else "—"
    color = "#27ae60" if (s['crec_feb_mar'] or 0) > 0 else "#e74c3c"
    inv_rows += f"""<tr>
        <td>{s['sku']}</td>
        <td>{s['desc'][:40]}</td>
        <td>{s['segmento']}</td>
        <td style="text-align:right">{fmt_clp(s['venta_feb'])}</td>
        <td style="text-align:right;font-weight:600">{fmt_clp(s['venta_mar'])}</td>
        <td style="color:{color};font-weight:700">{crec}</td>
    </tr>"""

# Digital campaign rows
dig_camp_rows = ""
for c in campanas_digitales:
    conv_color = "#27ae60" if c['tasa_conversion'] >= 5 else "#f39c12" if c['tasa_conversion'] >= 3 else "#e74c3c"
    dig_camp_rows += f"""<tr>
        <td><strong>{c['campana']}</strong></td>
        <td style="text-align:right">{c['visitas_catalogo']:,}</td>
        <td style="text-align:right">{c['clics_productos']:,}</td>
        <td style="text-align:right">{c['compras_post_clic']}</td>
        <td style="text-align:right;font-weight:600">{fmt_clp(c['venta_atribuida'])}</td>
        <td style="color:{conv_color};font-weight:700;text-align:right">{c['tasa_conversion']}%</td>
    </tr>"""

# Top productos digital rows
dig_prod_rows = ""
for p in top_productos_digital:
    dig_prod_rows += f"""<tr>
        <td>{p['sku']}</td>
        <td>{p['desc']}</td>
        <td><span class="badge">{p['campana']}</span></td>
        <td style="text-align:right">{p['clics']}</td>
        <td style="text-align:right">{p['compras']}</td>
        <td style="text-align:right;font-weight:600">{fmt_clp(p['venta'])}</td>
    </tr>"""

# Mailing rows
mailing_rows = ""
for m in mailing_list:
    mailing_rows += f"""<tr>
        <td>{m['fecha']}</td>
        <td><strong>{m['nombre']}</strong></td>
        <td style="text-align:right">{m['enviados']:,}</td>
        <td style="text-align:right">{m['aperturas']:,}</td>
        <td style="text-align:right;color:#27ae60;font-weight:600">{m['tasa_apertura']}%</td>
        <td style="text-align:right">{m['clics']:,}</td>
        <td style="text-align:right;color:#f39c12;font-weight:600">{m['tasa_clic']}%</td>
    </tr>"""

# Products detail rows from SKU data — build top labs summary
top_labs_summary = []
for lab in skus['top_laboratorios'][:12]:
    if lab['nombre'] == 'Sin laboratorio':
        continue
    top_labs_summary.append(lab)

prod_lab_rows = ""
for lab in top_labs_summary[:10]:
    prod_lab_rows += f"""<tr>
        <td><strong>{lab['nombre'][:35]}</strong></td>
        <td style="text-align:right">{lab['skus']}</td>
        <td style="text-align:right;font-weight:600">{lab['rotacion_3m']:,}</td>
        <td style="text-align:right">{round(lab['rotacion_3m']/lab['skus']) if lab['skus'] else 0:,}</td>
    </tr>"""

# JSON data for charts
month_labels = json.dumps([m['mes'] for m in meses])
month_ventas = json.dumps([round(m['ventas']/1_000_000) for m in meses])
month_unidades = json.dumps([m['unidades'] for m in meses])
month_camps = json.dumps([m['campanas'] for m in meses])

vis_mes_labels = json.dumps([v['mes'] for v in visitas_mensuales])
vis_mes_b2b = json.dumps([v['visitas_b2b'] for v in visitas_mensuales])
vis_mes_cat = json.dumps([v['visitas_catalogo'] for v in visitas_mensuales])
vis_mes_compras = json.dumps([v['compras'] for v in visitas_mensuales])
vis_mes_venta = json.dumps([round(v['venta_online']/1_000_000) for v in visitas_mensuales])

fuente_labels = json.dumps([f['fuente'] for f in visitas_fuente])
fuente_data = json.dumps([f['sesiones'] for f in visitas_fuente])

camp_dig_labels = json.dumps([c['campana'] for c in campanas_digitales])
camp_dig_visitas = json.dumps([c['visitas_catalogo'] for c in campanas_digitales])
camp_dig_clics = json.dumps([c['clics_productos'] for c in campanas_digitales])
camp_dig_compras = json.dumps([c['compras_post_clic'] for c in campanas_digitales])

# Mailing chart data
mailing_fechas = json.dumps([m['fecha'] for m in mailing_list])
mailing_tasas = json.dumps([m['tasa_apertura'] for m in mailing_list])

# ============================================================
# HTML
# ============================================================
HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ClinicalMarket — Dashboard Retail v8</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
:root {{
    --primary: #0DA7EE;
    --dark: #0688E2;
    --success: #27ae60;
    --danger: #e74c3c;
    --warning: #f39c12;
    --bg: #f5f7fa;
    --card: #ffffff;
    --text: #2c3e50;
    --muted: #7f8c8d;
    --border: #e8ecf1;
    --bg-dark: #1a1a2e;
    --card-dark: #16213e;
    --text-dark: #e0e0e0;
    --border-dark: #2a2a4a;
}}

* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Poppins',sans-serif; background:var(--bg); color:var(--text); font-size:14px; transition:background-color .3s, color .3s; }}
body.dark {{ background:var(--bg-dark); color:var(--text-dark); }}

.header {{ background:linear-gradient(135deg, var(--primary) 0%, var(--dark) 100%); color:white; padding:20px 28px; display:flex; justify-content:space-between; align-items:center; }}
.header-left h1 {{ font-size:22px; font-weight:800; }}
.header-sub {{ font-size:12px; opacity:.85; margin-top:4px; display:flex; gap:20px; flex-wrap:wrap; }}
.header-right {{ display:flex; gap:10px; align-items:center; }}

.theme-toggle {{
    background:rgba(255,255,255,.2);
    border:1px solid rgba(255,255,255,.3);
    color:white;
    padding:8px 12px;
    border-radius:6px;
    cursor:pointer;
    font-size:16px;
    transition:all .2s;
}}
.theme-toggle:hover {{ background:rgba(255,255,255,.3); }}

.print-btn {{
    background:rgba(255,255,255,.2);
    border:1px solid rgba(255,255,255,.3);
    color:white;
    padding:8px 12px;
    border-radius:6px;
    cursor:pointer;
    font-size:11px;
    font-weight:500;
    transition:all .2s;
    font-family:inherit;
}}
.print-btn:hover {{ background:rgba(255,255,255,.3); }}

.nav {{ background:var(--card); border-bottom:2px solid var(--border); padding:0 20px; display:flex; gap:0; overflow-x:auto; position:sticky; top:0; z-index:100; }}
body.dark .nav {{ background:var(--card-dark); border-bottom-color:var(--border-dark); }}

.nav button {{ padding:12px 16px; border:none; background:none; font-family:inherit; font-size:12px; font-weight:500; color:var(--muted); cursor:pointer; border-bottom:3px solid transparent; white-space:nowrap; transition:all .2s; }}
.nav button:hover {{ color:var(--text); }}
.nav button.active {{ color:var(--primary); border-bottom-color:var(--primary); font-weight:600; }}

.section {{ display:none; padding:20px 28px; max-width:1400px; margin:0 auto; }}
.section.active {{ display:block; }}

.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin:16px 0; }}
.kpi {{ background:var(--card); border-radius:10px; padding:16px; border-left:4px solid var(--primary); box-shadow:0 1px 3px rgba(0,0,0,.05); transition:all .3s; }}
body.dark .kpi {{ background:var(--card-dark); box-shadow:0 1px 3px rgba(0,0,0,.3); }}

.kpi-label {{ font-size:10px; text-transform:uppercase; letter-spacing:.5px; color:var(--muted); font-weight:600; }}
.kpi-value {{ font-size:24px; font-weight:800; color:var(--dark); margin:4px 0 2px; }}
.kpi-sub {{ font-size:11px; color:var(--muted); }}
.kpi-green {{ border-left-color:var(--success); }}
.kpi-green .kpi-value {{ color:var(--success); }}
.kpi-orange {{ border-left-color:var(--warning); }}
.kpi-orange .kpi-value {{ color:var(--warning); }}
.kpi-red {{ border-left-color:var(--danger); }}
.kpi-red .kpi-value {{ color:var(--danger); }}

.insight {{ background:#fffbeb; border-left:4px solid var(--warning); padding:12px 16px; border-radius:8px; margin:12px 0; font-size:12px; line-height:1.6; }}
body.dark .insight {{ background:rgba(243, 156, 18, .1); }}

.insight strong {{ color:var(--text); }}
.insight-blue {{ background:#eef6fd; border-left-color:var(--primary); }}
body.dark .insight-blue {{ background:rgba(13, 167, 238, .1); }}

.table-wrap {{ background:var(--card); border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.05); margin:12px 0; }}
body.dark .table-wrap {{ background:var(--card-dark); box-shadow:0 1px 3px rgba(0,0,0,.3); }}

.table-header {{ display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-bottom:1px solid var(--border); }}
body.dark .table-header {{ border-bottom-color:var(--border-dark); }}

.table-header h3 {{ font-size:14px; font-weight:600; }}
.row-count {{ font-size:11px; color:var(--muted); }}

table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th {{ background:#f8f9fb; padding:8px 12px; text-align:left; font-weight:600; font-size:10px; text-transform:uppercase; letter-spacing:.3px; color:var(--muted); border-bottom:1px solid var(--border); }}
body.dark th {{ background:var(--border-dark); color:var(--muted); }}

td {{ padding:8px 12px; border-bottom:1px solid #f2f4f7; }}
body.dark td {{ border-bottom-color:var(--border-dark); }}

tr:hover {{ background:#fafbfd; }}
body.dark tr:hover {{ background:rgba(255,255,255,.05); }}

.chart-box {{ background:var(--card); border-radius:10px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,.05); margin:12px 0; max-height:320px; }}
body.dark .chart-box {{ background:var(--card-dark); box-shadow:0 1px 3px rgba(0,0,0,.3); }}

.chart-box h3 {{ font-size:13px; font-weight:600; margin-bottom:8px; }}
.chart-row {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
@media(max-width:900px) {{ .chart-row {{ grid-template-columns:1fr; }} }}

.badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; background:#eef6fd; color:var(--primary); }}
.badge-green {{ background:#e8f8ef; color:var(--success); }}
.badge-red {{ background:#fdecea; color:var(--danger); }}

.btn {{ display:inline-flex; align-items:center; gap:5px; padding:6px 12px; border-radius:6px; border:1px solid var(--border); background:white; font-family:inherit; font-size:11px; font-weight:500; cursor:pointer; color:var(--text); transition:all .2s; }}
.btn:hover {{ background:var(--primary); color:white; border-color:var(--primary); }}
body.dark .btn {{ background:var(--card-dark); border-color:var(--border-dark); color:var(--text-dark); }}
body.dark .btn:hover {{ background:var(--primary); color:white; border-color:var(--primary); }}

.filter-bar {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin:10px 0; }}
.filter-bar input {{ padding:7px 12px; border:1px solid var(--border); border-radius:6px; font-family:inherit; font-size:12px; width:260px; background:var(--card); color:var(--text); }}
.filter-bar select {{ padding:7px 12px; border:1px solid var(--border); border-radius:6px; font-family:inherit; font-size:12px; background:var(--card); color:var(--text); }}
body.dark .filter-bar input {{ background:var(--card-dark); border-color:var(--border-dark); color:var(--text-dark); }}
body.dark .filter-bar select {{ background:var(--card-dark); border-color:var(--border-dark); color:var(--text-dark); }}

.funnel {{ display:flex; gap:0; align-items:stretch; margin:16px 0; }}
.funnel-step {{ flex:1; text-align:center; padding:12px 6px; position:relative; }}
.funnel-step:not(:last-child)::after {{ content:"→"; position:absolute; right:-10px; top:50%; transform:translateY(-50%); font-size:18px; color:var(--muted); z-index:1; }}
.funnel-bar {{ height:6px; border-radius:3px; margin:6px auto 0; }}
.funnel-label {{ font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:600; }}
.funnel-value {{ font-size:18px; font-weight:700; }}

.grid-3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }}
@media(max-width:900px) {{ .grid-3 {{ grid-template-columns:1fr; }} }}

.alerts-box {{ background:var(--card); border-radius:10px; padding:16px; margin:12px 0; border-left:4px solid var(--success); box-shadow:0 1px 3px rgba(0,0,0,.05); }}
body.dark .alerts-box {{ background:var(--card-dark); box-shadow:0 1px 3px rgba(0,0,0,.3); }}

.alert-item {{ padding:8px 0; border-bottom:1px solid var(--border); display:flex; justify-content:space-between; align-items:center; font-size:12px; }}
body.dark .alert-item {{ border-bottom-color:var(--border-dark); }}

.alert-item:last-child {{ border-bottom:none; }}
.alert-item strong {{ color:var(--dark); }}

.vendor-bar {{ display:flex; gap:8px; margin:8px 0; }}
.vendor-item {{ flex:1; text-align:center; padding:8px; background:#f8f9fb; border-radius:6px; font-size:11px; }}
body.dark .vendor-item {{ background:var(--border-dark); }}

.scroll-to-top {{
    position:fixed;
    bottom:20px;
    right:20px;
    width:40px;
    height:40px;
    background:var(--primary);
    color:white;
    border:none;
    border-radius:50%;
    cursor:pointer;
    display:none;
    align-items:center;
    justify-content:center;
    font-size:20px;
    box-shadow:0 4px 8px rgba(0,0,0,.2);
    transition:all .3s;
    z-index:999;
}}
.scroll-to-top:hover {{ transform:translateY(-3px); box-shadow:0 6px 12px rgba(0,0,0,.3); }}
.scroll-to-top.show {{ display:flex; }}

footer {{ background:#2c3e50; color:rgba(255,255,255,.7); padding:16px 28px; text-align:center; font-size:11px; margin-top:20px; }}
body.dark footer {{ background:#0f0f1e; }}

footer strong {{ color:white; }}
footer a {{ color:var(--primary); text-decoration:none; }}
footer a:hover {{ text-decoration:underline; }}

@media print {{ .nav, .btn, .filter-bar, footer, .theme-toggle, .print-btn, .scroll-to-top {{ display:none; }} .section {{ display:block !important; }} }}
</style>
</head>
<body>

<div class="header">
    <div class="header-left">
        <h1>ClinicalMarket B2B — Dashboard Retail v8</h1>
        <div class="header-sub">
            <span>Canal retail: farmacias, droguerías, pet shops, veterinarias</span>
            <span>Generado: {GENERATED_DATE}</span>
            <span>Fuentes: SAP · Power BI · GA4 · MailUp · Publitas</span>
        </div>
    </div>
    <div class="header-right">
        <button class="theme-toggle" id="themeToggle" title="Alternar modo oscuro">🌙</button>
        <button class="print-btn" onclick="window.print()" title="Imprimir dashboard">🖨 Imprimir</button>
    </div>
</div>

<div class="nav" id="nav">
    <button class="active" onclick="showTab('resumen')">Resumen</button>
    <button onclick="showTab('comparativo')">Comparativo</button>
    <button onclick="showTab('campanas')">Campañas</button>
    <button onclick="showTab('digital')">Digital</button>
    <button onclick="showTab('mailing')">Mailing</button>
    <button onclick="showTab('productos')">Productos</button>
    <button onclick="showTab('clientes')">Clientes</button>
</div>

<!-- ================================ RESUMEN ================================ -->
<div class="section active" id="resumen">
    <div class="insight">
        <strong>Dashboard para el equipo comercial.</strong> Aquí ves ventas, campañas, visitas al B2B y oportunidades.
        Los datos vienen de SAP (ventas), Power BI (campañas), GA4 (tráfico web) y MailUp (emails).
    </div>

    <h2 style="margin:16px 0 8px;font-size:16px">Marzo 2026 vs 2025</h2>
    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Venta Marzo 2026</div>
            <div class="kpi-value">{fmt_clp(venta_26)}</div>
            <div class="kpi-sub"><span style="color:{color_venta}">{arrow_venta} {crec_venta}%</span> vs Mar 2025 · <span class="badge">SAP</span></div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">Margen Bruto</div>
            <div class="kpi-value">{margen_26}%</div>
            <div class="kpi-sub">+5.6% vs 2025 · <span class="badge badge-green">SAP</span></div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Venta Acum. Retail</div>
            <div class="kpi-value">{fmt_clp(clientes['total_venta'])}</div>
            <div class="kpi-sub">{clientes['total_clientes']} clientes · 2025-2026</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Venta Campañas (6m)</div>
            <div class="kpi-value">{fmt_clp(total_ventas_6m)}</div>
            <div class="kpi-sub">{total_unid_6m:,} unid · {sum(m['campanas'] for m in meses)} campañas</div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi kpi-orange">
            <div class="kpi-label">Pareto (80% venta)</div>
            <div class="kpi-value">Top {clientes['pareto_n80']}</div>
            <div class="kpi-sub">{clientes['pareto_pct']}% de clientes = 80% ingreso</div>
        </div>
        <div class="kpi kpi-red">
            <div class="kpi-label">SKUs sin rotación</div>
            <div class="kpi-value">{skus['estados'].get('Nunca Rotados', 0):,}</div>
            <div class="kpi-sub">de {skus['total_skus']:,} totales</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Visitas B2B (Mar)</div>
            <div class="kpi-value">{total_visitas_b2b_mar:,}</div>
            <div class="kpi-sub">{visitas_mensuales[-1]['compras']} compras online · <span class="badge">GA4</span></div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Venta desde catálogos</div>
            <div class="kpi-value">{fmt_clp(total_venta_digital)}</div>
            <div class="kpi-sub">{total_compras_digital} compras post-clic · <span class="badge">GA4</span></div>
        </div>
    </div>

    <div class="chart-row">
        <div class="chart-box">
            <h3>Ventas Campañas por Mes ($M)</h3>
            <canvas id="chartVentas6m" height="100"></canvas>
        </div>
        <div class="chart-box">
            <h3>Visitas B2B vs Compras</h3>
            <canvas id="chartVisitasCompras" height="100"></canvas>
        </div>
    </div>

    <div class="insight-blue insight" style="margin-top:16px">
        <strong>Oportunidades:</strong><br>
        1. <strong>Clientes por activar:</strong> {clientes['total_clientes'] - clientes['pareto_n80']} clientes fuera del Pareto con potencial de crecimiento.<br>
        2. <strong>Catálogo:</strong> {skus['estados'].get('Nunca Rotados', 0):,} SKUs nunca vendidos — depurar o activar con campañas.<br>
        3. <strong>Campañas Invierno:</strong> Prep. Invierno lidera con {fmt_clp(camp_crecimiento[0]['venta_26'] if camp_crecimiento else 0)} en ventas.<br>
        4. <strong>Conversión digital:</strong> De {total_visitas_catalogo:,} visitas a catálogo, {total_compras_digital} se convirtieron en compra ({round(total_compras_digital/total_visitas_catalogo*100, 1)}%) — hay espacio para mejorar.
    </div>
</div>

<!-- ================================ COMPARATIVO ================================ -->
<div class="section" id="comparativo">
    <h2 style="font-size:16px">Comparativo Marzo 2025 vs 2026</h2>
    <div class="insight">Mismo mes, distinto año. Así se ve el crecimiento real sin estacionalidad.</div>

    <div class="kpi-grid">
        <div class="kpi {kpi_class_venta}">
            <div class="kpi-label">Cambio en Venta</div>
            <div class="kpi-value">{arrow_venta} {crec_venta}%</div>
            <div class="kpi-sub">{fmt_clp(venta_25)} → {fmt_clp(venta_26)}</div>
        </div>
        <div class="kpi {kpi_class_unid}">
            <div class="kpi-label">Cambio en Unidades</div>
            <div class="kpi-value">{arrow_unid} {crec_unid}%</div>
            <div class="kpi-sub">{unid_25:,} → {unid_26:,}</div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">Cambio en Margen</div>
            <div class="kpi-value">▲ +5.7%</div>
            <div class="kpi-sub">11.1% → {margen_26}%</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Campañas Mar 2026</div>
            <div class="kpi-value">8</div>
            <div class="kpi-sub">vs 0 especiales en Mar 2025</div>
        </div>
    </div>

    <div class="insight-blue insight">
        <strong>En simple:</strong> La venta se mantuvo (+0.1%) pero con menos unidades (-4.6%). Eso significa
        <strong>ticket promedio más alto</strong>. El margen subió +5.7% — se están vendiendo productos de mayor valor.
        Las campañas nuevas (Prep. Invierno, Invierno Vet, Dragpharma) compensaron la baja natural.
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Rendimiento por Campaña — Mar 2025 vs 2026</h3>
            <button class="btn" onclick="exportTable('tblCampComp','campanas_comparativo.csv')">Exportar CSV</button>
        </div>
        <table id="tblCampComp">
            <thead><tr><th>Campaña</th><th>SKUs</th><th>Venta 2025</th><th>Venta 2026</th><th>Diferencia</th><th>Movimiento SKUs</th></tr></thead>
            <tbody>{camp_rows_html}</tbody>
        </table>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Top 20 SKUs — Marzo 2026</h3>
            <button class="btn" onclick="exportTable('tblSkuComp','skus_comparativo.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar SKU o descripción..." id="filterSkuComp">
            <span class="row-count" id="rowCountSkuComp"></span>
        </div>
        <table id="tblSkuComp">
            <thead><tr><th>SKU</th><th>Descripción</th><th>Campaña</th><th>Venta 2025</th><th>Venta 2026</th><th>Crec.</th></tr></thead>
            <tbody>{sku_comp_rows}</tbody>
        </table>
    </div>
</div>

<!-- ================================ CAMPAÑAS ================================ -->
<div class="section" id="campanas">
    <h2 style="font-size:16px">Campañas — Ventas y Evolución</h2>
    <div class="insight">
        <strong>¿Qué ves aquí?</strong> Cada campaña del catálogo B2B, cuánto vendió por mes, y el detalle de la campaña de invierno.
        Los datos de venta vienen de Power BI/SAP. Para ver clics y visitas digitales de cada campaña, ve a la pestaña <strong>Digital</strong>.
    </div>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Venta Total 6 Meses</div>
            <div class="kpi-value">{fmt_clp(total_ventas_6m)}</div>
            <div class="kpi-sub">Oct 2025 — Mar 2026</div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">Mejor Mes</div>
            <div class="kpi-value">{best_month['mes']}</div>
            <div class="kpi-sub">{fmt_clp(best_month['ventas'])} · {best_month['unidades']:,} unidades</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Unidades Vendidas</div>
            <div class="kpi-value">{total_unid_6m:,}</div>
            <div class="kpi-sub">Promedio {round(total_unid_6m/6):,} por mes</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Ticket Promedio</div>
            <div class="kpi-value">{fmt_clp(round(total_ventas_6m / total_unid_6m))}</div>
            <div class="kpi-sub">Venta / unidad promedio</div>
        </div>
    </div>

    <div class="chart-row">
        <div class="chart-box">
            <h3>Ventas por Mes ($M)</h3>
            <canvas id="chartCampVentas" height="100"></canvas>
        </div>
        <div class="chart-box">
            <h3>Unidades y Campañas Activas</h3>
            <canvas id="chartCampUnid" height="100"></canvas>
        </div>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Campaña Invierno 2026 — Detalle Feb → Mar</h3>
            <button class="btn" onclick="exportTable('tblInvierno','invierno_2026.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar producto..." id="filterInvierno">
            <span class="row-count" id="rowCountInvierno"></span>
        </div>
        <table id="tblInvierno">
            <thead><tr><th>SKU</th><th>Producto</th><th>Segmento</th><th>Venta Feb</th><th>Venta Mar</th><th>Crec. Feb→Mar</th></tr></thead>
            <tbody>{inv_rows}</tbody>
        </table>
    </div>

    <div class="insight-blue insight">
        <strong>Resumen:</strong> Prep. Invierno lidera con 121 SKUs y {fmt_clp(camp_crecimiento[0]['venta_26'] if camp_crecimiento else 0)}.
        Diciembre fue el peak de ventas con {fmt_clp(115400000)} gracias a las campañas de fin de año.
    </div>
</div>

<!-- ================================ DIGITAL ================================ -->
<div class="section" id="digital">
    <h2 style="font-size:16px">Digital — Visitas, Catálogos y Conversión</h2>
    <div class="insight">
        <strong>¿Qué ves aquí?</strong> Todo el recorrido digital: cuánta gente visita el B2B, de dónde vienen,
        cuántos entran a los catálogos de campaña, cuántos hacen clic en productos y cuántos terminan comprando.
        Fuentes: GA4 (tráfico) + Publitas (catálogos).
    </div>

    <h3 style="margin:16px 0 8px;font-size:14px">Embudo Digital — Marzo 2026</h3>
    <div class="funnel">
        <div class="funnel-step">
            <div class="funnel-label">Visitas al B2B</div>
            <div class="funnel-value" style="color:var(--primary)">{total_visitas_b2b_mar:,}</div>
            <div class="funnel-bar" style="width:100%;background:var(--primary)"></div>
            <div style="font-size:10px;color:var(--muted);margin-top:4px">Usuarios que llegan</div>
        </div>
        <div class="funnel-step">
            <div class="funnel-label">Ven catálogos</div>
            <div class="funnel-value" style="color:var(--dark)">{total_visitas_catalogo:,}</div>
            <div class="funnel-bar" style="width:{round(total_visitas_catalogo/total_visitas_b2b_mar*100)}%;background:var(--dark)"></div>
            <div style="font-size:10px;color:var(--muted);margin-top:4px">{round(total_visitas_catalogo/total_visitas_b2b_mar*100)}% navega campañas</div>
        </div>
        <div class="funnel-step">
            <div class="funnel-label">Clic en productos</div>
            <div class="funnel-value" style="color:var(--warning)">{total_clics_productos:,}</div>
            <div class="funnel-bar" style="width:{round(total_clics_productos/total_visitas_b2b_mar*100)}%;background:var(--warning)"></div>
            <div style="font-size:10px;color:var(--muted);margin-top:4px">{round(total_clics_productos/total_visitas_b2b_mar*100)}% hace clic</div>
        </div>
        <div class="funnel-step">
            <div class="funnel-label">Compran</div>
            <div class="funnel-value" style="color:var(--success)">{total_compras_digital}</div>
            <div class="funnel-bar" style="width:{round(total_compras_digital/total_visitas_b2b_mar*100)}%;background:var(--success)"></div>
            <div style="font-size:10px;color:var(--muted);margin-top:4px">{round(total_compras_digital/total_visitas_b2b_mar*100, 1)}% convierte</div>
        </div>
        <div class="funnel-step">
            <div class="funnel-label">Venta generada</div>
            <div class="funnel-value" style="color:var(--dark)">{fmt_clp(total_venta_digital)}</div>
            <div class="funnel-bar" style="width:100%;background:var(--success)"></div>
            <div style="font-size:10px;color:var(--muted);margin-top:4px">Desde catálogos digitales</div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Visitas B2B (Mar)</div>
            <div class="kpi-value">{total_visitas_b2b_mar:,}</div>
            <div class="kpi-sub"><span class="badge">GA4</span></div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Visitas Catálogos</div>
            <div class="kpi-value">{total_visitas_catalogo:,}</div>
            <div class="kpi-sub">{round(total_visitas_catalogo/total_visitas_b2b_mar*100)}% del tráfico</div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">Clics en Productos</div>
            <div class="kpi-value">{total_clics_productos:,}</div>
            <div class="kpi-sub">{round(total_clics_productos/total_visitas_catalogo*100, 1)}% tasa de clic</div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">Compras Post-Clic</div>
            <div class="kpi-value">{total_compras_digital}</div>
            <div class="kpi-sub">{fmt_clp(total_venta_digital)} venta atribuida</div>
        </div>
    </div>

    <h3 style="margin:16px 0 8px;font-size:14px">¿De dónde vienen las visitas?</h3>
    <div class="chart-row">
        <div class="chart-box">
            <h3>Fuente de Tráfico</h3>
            <canvas id="chartFuente" height="100"></canvas>
        </div>
        <div class="chart-box">
            <h3>Visitas B2B vs Compras (mensual)</h3>
            <canvas id="chartVisMes" height="100"></canvas>
        </div>
    </div>

    <h3 style="margin:16px 0 8px;font-size:14px">Rendimiento por Campaña — Clics y Conversión</h3>
    <div class="table-wrap">
        <div class="table-header">
            <h3>Cada campaña: visitas al catálogo, clics en productos, compras y venta</h3>
            <button class="btn" onclick="exportTable('tblDigCamp','digital_campanas.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar campaña..." id="filterDigCamp">
            <span class="row-count" id="rowCountDigCamp"></span>
        </div>
        <table id="tblDigCamp">
            <thead><tr>
                <th>Campaña</th><th style="text-align:right">Visitas</th>
                <th style="text-align:right">Clics Productos</th><th style="text-align:right">Compras</th>
                <th style="text-align:right">Venta</th><th style="text-align:right">% Conversión</th>
            </tr></thead>
            <tbody>{dig_camp_rows}</tbody>
        </table>
    </div>

    <div class="chart-row">
        <div class="chart-box">
            <h3>Visitas vs Clics por Campaña</h3>
            <canvas id="chartDigCamp" height="100"></canvas>
        </div>
        <div class="chart-box">
            <h3>Compras por Campaña</h3>
            <canvas id="chartDigCompras" height="100"></canvas>
        </div>
    </div>

    <h3 style="margin:16px 0 8px;font-size:14px">Top 10 Productos Digitales — Más clics desde catálogo</h3>
    <div class="table-wrap">
        <div class="table-header">
            <h3>Productos que más se ven y compran desde los catálogos</h3>
            <button class="btn" onclick="exportTable('tblDigProd','digital_productos.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar producto o campaña..." id="filterDigProd">
            <span class="row-count" id="rowCountDigProd"></span>
        </div>
        <table id="tblDigProd">
            <thead><tr><th>SKU</th><th>Producto</th><th>Campaña</th><th style="text-align:right">Clics</th><th style="text-align:right">Compras</th><th style="text-align:right">Venta</th></tr></thead>
            <tbody>{dig_prod_rows}</tbody>
        </table>
    </div>

    <div class="kpi-grid" style="margin-top:16px">
        <div class="kpi">
            <div class="kpi-label">Email — Tasa Apertura</div>
            <div class="kpi-value">{mailing['tasa_apertura']}%</div>
            <div class="kpi-sub">{mailing['enviados']:,} envíos · {mailing['clics']} clics · <span class="badge">MailUp</span></div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Sesiones desde Email</div>
            <div class="kpi-value">{mailing['sesiones_email']:,}</div>
            <div class="kpi-sub">Tráfico generado por campañas de email</div>
        </div>
    </div>

    <div class="insight-blue insight" style="margin-top:12px">
        <strong>Lectura rápida:</strong><br>
        — De cada 100 visitas al B2B, {round(total_visitas_catalogo/total_visitas_b2b_mar*100)} entran a catálogos de campaña y {round(total_compras_digital/total_visitas_b2b_mar*100, 1)} terminan comprando.<br>
        — <strong>Dragpharma</strong> tiene la mayor tasa de conversión ({campanas_digitales[3]['tasa_conversion']}%) con menos visitas — el tráfico que llega es más calificado.<br>
        — <strong>Prep. Invierno</strong> lidera en volumen: {campanas_digitales[0]['visitas_catalogo']} visitas y {fmt_clp(campanas_digitales[0]['venta_atribuida'])} en ventas.<br>
        — El email sigue siendo el 2do canal más fuerte ({mailing['sesiones_email']:,} sesiones). Mejorar la tasa de clic (hoy {mailing['tasa_clic']}%) amplificaría el impacto.
    </div>
</div>

<!-- ================================ MAILING ================================ -->
<div class="section" id="mailing">
    <h2 style="font-size:16px">Email Marketing — Campañas y Rendimiento</h2>
    <div class="insight">
        <strong>¿Qué ves aquí?</strong> Historial completo de campañas de email, tasa de apertura, clics y engagement.
        Los datos vienen de MailUp. Cada campaña es monitoreada para entender qué mensajes resuenan mejor con tu audiencia.
    </div>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Total Enviados</div>
            <div class="kpi-value">{total_enviados:,}</div>
            <div class="kpi-sub">Últimas {len(mailing_list)} campañas</div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">Promedio Apertura</div>
            <div class="kpi-value">{avg_tasa_apertura}%</div>
            <div class="kpi-sub">Tasa de apertura promedio</div>
        </div>
        <div class="kpi kpi-orange">
            <div class="kpi-label">Promedio Clics</div>
            <div class="kpi-value">{avg_tasa_clic}%</div>
            <div class="kpi-sub">Tasa de clic promedio</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Última Campaña</div>
            <div class="kpi-value">{mailing['ultima_campana']}</div>
            <div class="kpi-sub">{mailing['enviados']:,} envíos · {mailing['tasa_apertura']}% apertura</div>
        </div>
    </div>

    <div class="chart-box">
        <h3>Tasa de Apertura por Campaña</h3>
        <canvas id="chartMailingTasas" height="100"></canvas>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Historial de Campañas</h3>
            <button class="btn" onclick="exportTable('tblMailing','mailing_campanas.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar campaña..." id="filterMailing">
            <span class="row-count" id="rowCountMailing"></span>
        </div>
        <table id="tblMailing">
            <thead><tr><th>Fecha</th><th>Campaña</th><th style="text-align:right">Enviados</th><th style="text-align:right">Aperturas</th><th style="text-align:right">% Apertura</th><th style="text-align:right">Clics</th><th style="text-align:right">% Clics</th></tr></thead>
            <tbody>{mailing_rows}</tbody>
        </table>
    </div>

    <div class="insight-blue insight">
        <strong>Recomendaciones:</strong><br>
        — La tasa de apertura promedio es {avg_tasa_apertura}%. Campañas con asunto corto y personalizadas tienden a superar este promedio.<br>
        — La tasa de clic promedio es {avg_tasa_clic}%. Mejorar el CTA (call-to-action) y la relevancia del contenido puede aumentar este indicador.<br>
        — Monitorear las campañas que superan ambos promedios para identificar patrones en asunto, horario de envío y segmentación.<br>
        — Considerar A/B testing en asuntos y contenido para optimizar engagement.
    </div>
</div>

<!-- ================================ PRODUCTOS ================================ -->
<div class="section" id="productos">
    <h2 style="font-size:16px">Productos — Estado del Catálogo</h2>
    <div class="insight">
        El catálogo completo tiene {skus['total_skus']:,} SKUs. Aquí ves cuántos se venden, cuántos están abandonados,
        quiebres de stock y qué laboratorios mueven más unidades.
    </div>

    <div class="kpi-grid">
        <div class="kpi kpi-green">
            <div class="kpi-label">Con Rotación</div>
            <div class="kpi-value">{skus['estados'].get('Con Rotación', 0):,}</div>
            <div class="kpi-sub">Vendidos en últimos 3 meses ({round(skus['estados'].get('Con Rotación',0)/skus['total_skus']*100)}%)</div>
        </div>
        <div class="kpi kpi-orange">
            <div class="kpi-label">Abandonados</div>
            <div class="kpi-value">{skus['estados'].get('Abandonados', 0):,}</div>
            <div class="kpi-sub">Antes vendían, ahora no ({round(skus['estados'].get('Abandonados',0)/skus['total_skus']*100)}%)</div>
        </div>
        <div class="kpi kpi-red">
            <div class="kpi-label">Nunca Vendidos</div>
            <div class="kpi-value">{skus['estados'].get('Nunca Rotados', 0):,}</div>
            <div class="kpi-sub">0 ventas en 12 meses ({round(skus['estados'].get('Nunca Rotados',0)/skus['total_skus']*100)}%)</div>
        </div>
        <div class="kpi kpi-red">
            <div class="kpi-label">Quiebres de Stock</div>
            <div class="kpi-value">{skus['quiebres_stock']:,}</div>
            <div class="kpi-sub">SKUs sin stock disponible</div>
        </div>
    </div>

    <div class="chart-row">
        <div class="chart-box">
            <h3>Estado del Catálogo</h3>
            <canvas id="chartSKU" height="100"></canvas>
        </div>
        <div class="chart-box">
            <h3>Proporción de SKUs</h3>
            <canvas id="chartSKUBar" height="100"></canvas>
        </div>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Top Laboratorios por Rotación (3 meses)</h3>
            <button class="btn" onclick="exportTable('tblProdLab','laboratorios_rotacion.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar laboratorio..." id="filterProdLab">
            <span class="row-count" id="rowCountProdLab"></span>
        </div>
        <table id="tblProdLab">
            <thead><tr><th>Laboratorio</th><th style="text-align:right">SKUs</th><th style="text-align:right">Rotación 3M (unid)</th><th style="text-align:right">Rotación/SKU</th></tr></thead>
            <tbody>{prod_lab_rows}</tbody>
        </table>
    </div>

    <div class="insight-blue insight">
        <strong>Oportunidades:</strong><br>
        — <strong>{skus['estados'].get('Nunca Rotados', 0):,} SKUs</strong> ({round(skus['estados'].get('Nunca Rotados', 0)/skus['total_skus']*100)}% del catálogo) nunca se han vendido. Depurar mejoraría la búsqueda para clientes.<br>
        — <strong>{skus['estados'].get('Abandonados', 0):,} abandonados</strong> son candidatos a reactivación con campañas especiales.<br>
        — <strong>{skus['quiebres_stock']:,} quiebres de stock</strong> significan venta perdida — priorizar reposición de los que más rotan.
    </div>
</div>

<!-- ================================ CLIENTES ================================ -->
<div class="section" id="clientes">
    <h2 style="font-size:16px">Clientes Retail</h2>
    <div class="insight">Base de clientes retail con compras 2025-2026. Solo canal: Ecommerce B2B + Retail + Retail Zona Extrema.</div>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Total Clientes</div>
            <div class="kpi-value">{clientes['total_clientes']}</div>
            <div class="kpi-sub">Con compra en 2025-2026</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Venta Total</div>
            <div class="kpi-value">{fmt_clp(clientes['total_venta'])}</div>
            <div class="kpi-sub">Acumulado 2025-2026</div>
        </div>
        <div class="kpi kpi-orange">
            <div class="kpi-label">Pareto 80%</div>
            <div class="kpi-value">Top {clientes['pareto_n80']}</div>
            <div class="kpi-sub">{clientes['pareto_pct']}% de la base = 80% del ingreso</div>
        </div>
    </div>

    <div class="alerts-box">
        <h3 style="font-size:13px;margin-bottom:12px;color:var(--dark)">Top 5 Clientes Estratégicos (Pareto)</h3>
        <div class="alert-item" style="padding-bottom:8px;margin-bottom:8px;border-bottom:1px solid var(--border)">
            <strong>{clientes['top50'][0]['nombre']}</strong>
            <span style="color:var(--success)">{fmt_clp(clientes['top50'][0]['venta_total'])}</span>
        </div>
        <div class="alert-item" style="padding-bottom:8px;margin-bottom:8px;border-bottom:1px solid var(--border)">
            <strong>{clientes['top50'][1]['nombre']}</strong>
            <span style="color:var(--success)">{fmt_clp(clientes['top50'][1]['venta_total'])}</span>
        </div>
        <div class="alert-item" style="padding-bottom:8px;margin-bottom:8px;border-bottom:1px solid var(--border)">
            <strong>{clientes['top50'][2]['nombre']}</strong>
            <span style="color:var(--success)">{fmt_clp(clientes['top50'][2]['venta_total'])}</span>
        </div>
        <div class="alert-item" style="padding-bottom:8px;margin-bottom:8px;border-bottom:1px solid var(--border)">
            <strong>{clientes['top50'][3]['nombre']}</strong>
            <span style="color:var(--success)">{fmt_clp(clientes['top50'][3]['venta_total'])}</span>
        </div>
        <div class="alert-item">
            <strong>{clientes['top50'][4]['nombre']}</strong>
            <span style="color:var(--success)">{fmt_clp(clientes['top50'][4]['venta_total'])}</span>
        </div>
    </div>

    <div class="alerts-box">
        <h3 style="font-size:13px;margin-bottom:12px;color:var(--dark)">Distribución por Vendedor</h3>
        <div class="vendor-bar">
            {''.join(f'<div class="vendor-item"><div style="font-weight:600">{len([c for c in clientes["top50"] if c["vendedor"] == v["nombre"]])}</div><div>{v["nombre"]}</div></div>' for v in clientes['vendedores'][:5])}
        </div>
    </div>

    <div class="chart-box">
        <h3>Distribución Pareto</h3>
        <canvas id="chartPareto" height="120"></canvas>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Top 30 Clientes</h3>
            <button class="btn" onclick="exportTable('tblClientes','clientes_retail.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar cliente o vendedor..." id="filterClientes">
            <select id="filterVendedor">
                <option value="">Todos los vendedores</option>
                {''.join(f'<option value="{v["nombre"]}">{v["nombre"]}</option>' for v in clientes['vendedores'])}
            </select>
            <span class="row-count" id="rowCountClientes"></span>
        </div>
        <table id="tblClientes">
            <thead><tr><th>#</th><th>Cliente</th><th>Vendedor</th><th style="text-align:right">Venta Total</th><th>% Total</th></tr></thead>
            <tbody>{cli_rows}</tbody>
        </table>
    </div>
</div>

<!-- ================================ FOOTER ================================ -->
<footer>
    <strong>ClinicalMarket B2B</strong> — Dashboard Retail v8<br>
    Generado: {GENERATED_DATE} · Fuentes: SAP, Power BI, GA4, MailUp, Publitas<br>
    Ecosistema ClinicalMarket / Gesmed / Profar · Rodrigo Arévalo
</footer>

<!-- Scroll to Top Button -->
<button class="scroll-to-top" id="scrollToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<!-- ================================ SCRIPTS ================================ -->
<script>
// Dark mode toggle
var darkMode = false;
var themeToggle = document.getElementById('themeToggle');
themeToggle.addEventListener('click', function() {{
    darkMode = !darkMode;
    if (darkMode) {{
        document.body.classList.add('dark');
        themeToggle.textContent = '☀️';
    }} else {{
        document.body.classList.remove('dark');
        themeToggle.textContent = '🌙';
    }}
}});

// Scroll to top button visibility
window.addEventListener('scroll', function() {{
    var btn = document.getElementById('scrollToTop');
    if (window.scrollY > 300) {{
        btn.classList.add('show');
    }} else {{
        btn.classList.remove('show');
    }}
}});

// URL hash navigation
window.addEventListener('hashchange', function() {{
    var hash = window.location.hash.substring(1) || 'resumen';
    showTab(hash);
}});

// Tab switching with hash support
function showTab(id) {{
    document.querySelectorAll('.section').forEach(function(s) {{ s.classList.remove('active'); }});
    document.querySelectorAll('.nav button').forEach(function(b) {{ b.classList.remove('active'); }});
    var section = document.getElementById(id);
    if (section) {{
        section.classList.add('active');
        window.location.hash = id;
        // Find matching button
        var buttons = document.querySelectorAll('.nav button');
        var tabMap = {{'resumen': 0, 'comparativo': 1, 'campanas': 2, 'digital': 3, 'mailing': 4, 'productos': 5, 'clientes': 6}};
        if (tabMap[id] !== undefined) {{
            buttons[tabMap[id]].classList.add('active');
        }}
        // Init charts
        setTimeout(function() {{ initCharts(); }}, 100);
    }}
}}

// Generic table text filter — bind to input fields
function setupFilter(inputId, tableId, rowCountId) {{
    var input = document.getElementById(inputId);
    if (!input) return;
    input.addEventListener('input', function() {{
        var q = this.value.toLowerCase();
        var rows = document.querySelectorAll('#' + tableId + ' tbody tr');
        var visibleCount = 0;
        for (var i = 0; i < rows.length; i++) {{
            var isMatch = rows[i].textContent.toLowerCase().indexOf(q) !== -1;
            rows[i].style.display = isMatch ? '' : 'none';
            if (isMatch) visibleCount++;
        }}
        if (rowCountId) {{
            document.getElementById(rowCountId).textContent = 'Mostrando ' + visibleCount + ' de ' + rows.length;
        }}
    }});
}}

// Column filter (select dropdown)
function setupColFilter(selectId, tableId, colIdx) {{
    var sel = document.getElementById(selectId);
    if (!sel) return;
    sel.addEventListener('change', function() {{
        var val = this.value;
        var rows = document.querySelectorAll('#' + tableId + ' tbody tr');
        for (var i = 0; i < rows.length; i++) {{
            if (!val) {{ rows[i].style.display = ''; continue; }}
            var cell = rows[i].cells[colIdx];
            rows[i].style.display = (cell && cell.textContent.trim() === val) ? '' : 'none';
        }}
    }});
}}

// CSV Export
function exportTable(tableId, filename) {{
    var table = document.getElementById(tableId);
    if (!table) return;
    var csv = [];
    var rows = table.querySelectorAll('tr');
    for (var i = 0; i < rows.length; i++) {{
        if (rows[i].style.display === 'none') continue;
        var cols = [];
        var cells = rows[i].querySelectorAll('th, td');
        for (var j = 0; j < cells.length; j++) {{
            cols.push('"' + cells[j].textContent.replace(/"/g, '""') + '"');
        }}
        csv.push(cols.join(','));
    }}
    var blob = new Blob([csv.join('\\n')], {{type: 'text/csv;charset=utf-8;'}});
    var link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}}

// KPI value animation with IntersectionObserver
function animateKPIValues() {{
    var kpis = document.querySelectorAll('.kpi-value');
    var observer = new IntersectionObserver(function(entries) {{
        entries.forEach(function(entry) {{
            if (entry.isIntersecting && !entry.target.dataset.animated) {{
                entry.target.dataset.animated = true;
                // Could add animation logic here if needed
            }}
        }});
    }}, {{threshold: 0.5}});
    kpis.forEach(function(kpi) {{ observer.observe(kpi); }});
}}

// ============= CHARTS =============
var chartsInit = false;
function initCharts() {{
    if (chartsInit) return;
    chartsInit = true;

    var C = {{
        primary: '#0DA7EE', dark: '#0688E2', success: '#27ae60',
        danger: '#e74c3c', warning: '#f39c12', purple: '#9b59b6'
    }};

    var chartOpts = {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ bodyFont: {{ size: 11 }} }} }},
        scales: {{ x: {{ ticks: {{ font: {{ size: 10 }} }} }}, y: {{ ticks: {{ font: {{ size: 10 }} }} }} }}
    }};

    // Resumen: Ventas 6m
    if (!window.chart_ventas6m && document.getElementById('chartVentas6m')) {{
        window.chart_ventas6m = new Chart(document.getElementById('chartVentas6m'), {{
            type: 'line',
            data: {{
                labels: {month_labels},
                datasets: [{{
                    label: 'Ventas ($M)',
                    data: {month_ventas},
                    borderColor: C.primary,
                    backgroundColor: C.primary + '22',
                    fill: true, tension: 0.3, pointRadius: 4, pointBackgroundColor: C.primary
                }}]
            }},
            options: chartOpts
        }});
    }}

    // Resumen: Visitas vs Compras
    if (!window.chart_visitascompras && document.getElementById('chartVisitasCompras')) {{
        window.chart_visitascompras = new Chart(document.getElementById('chartVisitasCompras'), {{
            type: 'bar',
            data: {{
                labels: {vis_mes_labels},
                datasets: [
                    {{ label: 'Visitas B2B', data: {vis_mes_b2b}, backgroundColor: C.primary + '99', borderRadius: 4, yAxisID: 'y' }},
                    {{ label: 'Compras', data: {vis_mes_compras}, type: 'line', borderColor: C.success, pointBackgroundColor: C.success, yAxisID: 'y1', tension: 0.3, pointRadius: 4 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ display: true, labels: {{ font: {{ size: 10 }} }} }} }},
                scales: {{
                    y: {{ position: 'left', ticks: {{ font: {{ size: 10 }} }} }},
                    y1: {{ position: 'right', grid: {{ drawOnChartArea: false }}, ticks: {{ font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}

    // Campañas: Ventas por mes
    if (!window.chart_campventas && document.getElementById('chartCampVentas')) {{
        window.chart_campventas = new Chart(document.getElementById('chartCampVentas'), {{
            type: 'bar',
            data: {{
                labels: {month_labels},
                datasets: [{{
                    label: 'Ventas ($M)',
                    data: {month_ventas},
                    backgroundColor: [C.primary, C.dark, C.success, C.warning, C.danger, C.purple],
                    borderRadius: 4
                }}]
            }},
            options: chartOpts
        }});
    }}

    // Campañas: Unidades + Campañas
    if (!window.chart_campunid && document.getElementById('chartCampUnid')) {{
        window.chart_campunid = new Chart(document.getElementById('chartCampUnid'), {{
            type: 'line',
            data: {{
                labels: {month_labels},
                datasets: [
                    {{ label:'Unidades', data:{month_unidades}, borderColor:C.primary, yAxisID:'y', tension:0.3, pointRadius:3 }},
                    {{ label:'Campañas', data:{month_camps}, borderColor:C.warning, yAxisID:'y1', tension:0.3, borderDash:[5,5], pointRadius:3 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ display: true, labels: {{ font: {{ size: 10 }} }} }} }},
                scales: {{
                    y: {{ position:'left', ticks: {{ font: {{ size: 10 }} }} }},
                    y1: {{ position:'right', grid:{{ drawOnChartArea:false }}, ticks: {{ font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}

    // Pareto
    if (!window.chart_pareto && document.getElementById('chartPareto')) {{
        var n = {clientes['total_clientes']};
        var pareto = {clientes['pareto_n80']};
        window.chart_pareto = new Chart(document.getElementById('chartPareto'), {{
            type: 'doughnut',
            data: {{
                labels: ['Top ' + pareto + ' (80% venta)', 'Resto ' + (n - pareto) + ' (20% venta)'],
                datasets: [{{ data: [pareto, n - pareto], backgroundColor: [C.primary, '#e8ecf1'], borderWidth: 0 }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, cutout: '65%', plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }} }} }} }} }}
        }});
    }}

    // SKU estados doughnut
    if (!window.chart_sku && document.getElementById('chartSKU')) {{
        window.chart_sku = new Chart(document.getElementById('chartSKU'), {{
            type: 'doughnut',
            data: {{
                labels: ['Con Rotación ({skus["estados"].get("Con Rotación",0):,})', 'Abandonados ({skus["estados"].get("Abandonados",0):,})', 'Nunca Vendidos ({skus["estados"].get("Nunca Rotados",0):,})'],
                datasets: [{{ data: [{skus['estados'].get('Con Rotación',0)}, {skus['estados'].get('Abandonados',0)}, {skus['estados'].get('Nunca Rotados',0)}],
                    backgroundColor: [C.success, C.warning, C.danger], borderWidth: 0 }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, cutout: '60%', plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }} }} }} }} }}
        }});
    }}

    // SKU bar chart
    if (!window.chart_skubar && document.getElementById('chartSKUBar')) {{
        window.chart_skubar = new Chart(document.getElementById('chartSKUBar'), {{
            type: 'bar',
            data: {{
                labels: ['Con Rotación', 'Abandonados', 'Nunca Vendidos', 'Quiebres Stock'],
                datasets: [{{ data: [{skus['estados'].get('Con Rotación',0)}, {skus['estados'].get('Abandonados',0)}, {skus['estados'].get('Nunca Rotados',0)}, {skus['quiebres_stock']}],
                    backgroundColor: [C.success, C.warning, C.danger, '#95a5a6'], borderRadius: 4 }}]
            }},
            options: chartOpts
        }});
    }}

    // Digital: Fuente de tráfico
    if (!window.chart_fuente && document.getElementById('chartFuente')) {{
        window.chart_fuente = new Chart(document.getElementById('chartFuente'), {{
            type: 'doughnut',
            data: {{
                labels: {fuente_labels},
                datasets: [{{ data: {fuente_data}, backgroundColor: [C.primary, C.warning, C.dark, C.success, C.purple], borderWidth: 0 }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: false, cutout: '55%', plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 9 }} }} }} }} }}
        }});
    }}

    // Digital: Visitas vs Compras mensual
    if (!window.chart_vismes && document.getElementById('chartVisMes')) {{
        window.chart_vismes = new Chart(document.getElementById('chartVisMes'), {{
            type: 'bar',
            data: {{
                labels: {vis_mes_labels},
                datasets: [
                    {{ label: 'Visitas Catálogo', data: {vis_mes_cat}, backgroundColor: C.primary + '88', borderRadius: 4, yAxisID: 'y' }},
                    {{ label: 'Compras', data: {vis_mes_compras}, type: 'line', borderColor: C.success, pointBackgroundColor: C.success, yAxisID: 'y1', tension: 0.3, pointRadius: 3 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ display: true, labels: {{ font: {{ size: 9 }} }} }} }},
                scales: {{
                    y: {{ position: 'left', ticks: {{ font: {{ size: 10 }} }} }},
                    y1: {{ position: 'right', grid: {{ drawOnChartArea: false }}, ticks: {{ font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}

    // Digital: Campañas visitas vs clics
    if (!window.chart_digcamp && document.getElementById('chartDigCamp')) {{
        window.chart_digcamp = new Chart(document.getElementById('chartDigCamp'), {{
            type: 'bar',
            data: {{
                labels: {camp_dig_labels},
                datasets: [
                    {{ label: 'Visitas Catálogo', data: {camp_dig_visitas}, backgroundColor: C.primary + '88', borderRadius: 4 }},
                    {{ label: 'Clics Productos', data: {camp_dig_clics}, backgroundColor: C.warning + '88', borderRadius: 4 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: {{ legend: {{ display: true, labels: {{ font: {{ size: 9 }} }} }} }},
                scales: {{ x: {{ ticks: {{ font: {{ size: 10 }} }} }}, y: {{ ticks: {{ font: {{ size: 9 }} }} }} }}
            }}
        }});
    }}

    // Digital: Compras por campaña
    if (!window.chart_digcompras && document.getElementById('chartDigCompras')) {{
        window.chart_digcompras = new Chart(document.getElementById('chartDigCompras'), {{
            type: 'bar',
            data: {{
                labels: {camp_dig_labels},
                datasets: [{{ label: 'Compras', data: {camp_dig_compras}, backgroundColor: C.success + 'cc', borderRadius: 4 }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ x: {{ ticks: {{ font: {{ size: 10 }} }} }}, y: {{ ticks: {{ font: {{ size: 9 }} }} }} }}
            }}
        }});
    }}

    // Mailing: Tasa de apertura por campaña
    if (!window.chart_mailingtasas && document.getElementById('chartMailingTasas')) {{
        window.chart_mailingtasas = new Chart(document.getElementById('chartMailingTasas'), {{
            type: 'line',
            data: {{
                labels: {mailing_fechas},
                datasets: [{{
                    label: 'Tasa Apertura (%)',
                    data: {mailing_tasas},
                    borderColor: C.success,
                    backgroundColor: C.success + '22',
                    fill: true, tension: 0.3, pointRadius: 4, pointBackgroundColor: C.success
                }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }}, tooltip: {{ bodyFont: {{ size: 11 }} }} }},
                scales: {{ x: {{ ticks: {{ font: {{ size: 10 }} }} }}, y: {{ ticks: {{ font: {{ size: 10 }} }} }} }}
            }}
        }});
    }}
}}

// ============= INIT =============
document.addEventListener('DOMContentLoaded', function() {{
    // Setup all filters with row count
    setupFilter('filterSkuComp', 'tblSkuComp', 'rowCountSkuComp');
    setupFilter('filterInvierno', 'tblInvierno', 'rowCountInvierno');
    setupFilter('filterDigCamp', 'tblDigCamp', 'rowCountDigCamp');
    setupFilter('filterDigProd', 'tblDigProd', 'rowCountDigProd');
    setupFilter('filterProdLab', 'tblProdLab', 'rowCountProdLab');
    setupFilter('filterClientes', 'tblClientes', 'rowCountClientes');
    setupFilter('filterMailing', 'tblMailing', 'rowCountMailing');
    setupColFilter('filterVendedor', 'tblClientes', 2);

    // Initialize row counts
    document.getElementById('rowCountSkuComp').textContent = 'Mostrando 20 de 20';
    document.getElementById('rowCountInvierno').textContent = 'Mostrando ' + document.querySelectorAll('#tblInvierno tbody tr').length + ' de ' + document.querySelectorAll('#tblInvierno tbody tr').length;
    document.getElementById('rowCountDigCamp').textContent = 'Mostrando ' + document.querySelectorAll('#tblDigCamp tbody tr').length + ' de ' + document.querySelectorAll('#tblDigCamp tbody tr').length;
    document.getElementById('rowCountDigProd').textContent = 'Mostrando ' + document.querySelectorAll('#tblDigProd tbody tr').length + ' de ' + document.querySelectorAll('#tblDigProd tbody tr').length;
    document.getElementById('rowCountProdLab').textContent = 'Mostrando ' + document.querySelectorAll('#tblProdLab tbody tr').length + ' de ' + document.querySelectorAll('#tblProdLab tbody tr').length;
    document.getElementById('rowCountClientes').textContent = 'Mostrando ' + document.querySelectorAll('#tblClientes tbody tr').length + ' de ' + document.querySelectorAll('#tblClientes tbody tr').length;
    document.getElementById('rowCountMailing').textContent = 'Mostrando ' + document.querySelectorAll('#tblMailing tbody tr').length + ' de ' + document.querySelectorAll('#tblMailing tbody tr').length;

    // Animate KPI values
    animateKPIValues();

    // Init charts after small delay
    setTimeout(function() {{ initCharts(); }}, 200);

    // Check for URL hash on load
    var hash = window.location.hash.substring(1);
    if (hash && hash !== 'resumen') {{
        showTab(hash);
    }}
}});
</script>

</body>
</html>
"""

# Write output
DOCS_DIR = os.path.join(DATA_DIR, '..', 'docs')
os.makedirs(DOCS_DIR, exist_ok=True)
output = os.path.join(DOCS_DIR, 'index.html')
with open(output, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"Dashboard v8: {output}")
print(f"Size: {len(HTML)/1024:.1f} KB, {HTML.count(chr(10))} lines")
print(f"Data sources: clientes_data, comparativo, sku_data, campanas_mensuales, ga4_visitas, campanas_digitales, productos_digital, mailing")
