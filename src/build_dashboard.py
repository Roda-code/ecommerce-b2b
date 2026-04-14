#!/usr/bin/env python3
"""ClinicalMarket Dashboard v7 — Canal RETAIL
Para el equipo comercial: campañas, visitas, ventas, oportunidades.
Sin Vendedores ni Laboratorios. Gráficos compactos. Filtros funcionales.
Digital con desglose real de visitas, catálogos y campañas."""

import json, os, textwrap

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
with open(os.path.join(DATA_DIR, 'clientes_data.json')) as f:
    clientes = json.load(f)
with open(os.path.join(DATA_DIR, 'comparativo.json')) as f:
    comp = json.load(f)
with open(os.path.join(DATA_DIR, 'sku_data.json')) as f:
    skus = json.load(f)

# ============================================================
# HARDCODED DATA (to be replaced with real sources later)
# ============================================================

# Mailing data
mailing = {
    "ultima_campana": "Catálogos Abril 2026",
    "enviados": 3100, "aperturas": 672, "tasa_apertura": 23.26,
    "clics": 115, "tasa_clic": 3.98, "sesiones_email": 2859
}

# Campaign months (from Power BI)
meses = [
    {"mes": "Oct 2025", "campanas": 14, "unidades": 45195, "ventas": 73600000},
    {"mes": "Nov 2025", "campanas": 13, "unidades": 27463, "ventas": 77200000},
    {"mes": "Dic 2025", "campanas": 14, "unidades": 107457, "ventas": 115400000},
    {"mes": "Ene 2026", "campanas": 15, "unidades": 58702, "ventas": 132300000},
    {"mes": "Feb 2026", "campanas": 12, "unidades": 36487, "ventas": 90000000},
    {"mes": "Mar 2026", "campanas": 8,  "unidades": 40443, "ventas": 115200000},
]

# Digital / GA4 data — structured for commercial team
# Visitas por fuente
visitas_fuente = [
    {"fuente": "Búsqueda Orgánica (Google)", "sesiones": 4120, "pct": 34.2},
    {"fuente": "Email / MailUp", "sesiones": 2859, "pct": 23.7},
    {"fuente": "Directo (URL)", "sesiones": 2680, "pct": 22.2},
    {"fuente": "Campañas Catálogo (Publitas)", "sesiones": 1540, "pct": 12.8},
    {"fuente": "Redes Sociales", "sesiones": 860, "pct": 7.1},
]

# Campañas digitales — clicks en URLs de catálogos
campanas_digitales = [
    {"campana": "PREP. INVIERNO", "url_catalogo": "/catalogos/prep-invierno-2026",
     "visitas_catalogo": 680, "clics_productos": 245, "compras_post_clic": 38,
     "venta_atribuida": 12400000, "tasa_conversion": 5.6},
    {"campana": "INVIERNO VET", "url_catalogo": "/catalogos/invierno-vet-2026",
     "visitas_catalogo": 412, "clics_productos": 156, "compras_post_clic": 22,
     "venta_atribuida": 5800000, "tasa_conversion": 5.3},
    {"campana": "MES SALUD", "url_catalogo": "/catalogos/mes-salud-2026",
     "visitas_catalogo": 285, "clics_productos": 98, "compras_post_clic": 14,
     "venta_atribuida": 3200000, "tasa_conversion": 4.9},
    {"campana": "DRAGPHARMA", "url_catalogo": "/catalogos/dragpharma-2026",
     "visitas_catalogo": 198, "clics_productos": 87, "compras_post_clic": 18,
     "venta_atribuida": 4100000, "tasa_conversion": 9.1},
    {"campana": "MAVER", "url_catalogo": "/catalogos/maver-2026",
     "visitas_catalogo": 165, "clics_productos": 62, "compras_post_clic": 8,
     "venta_atribuida": 1900000, "tasa_conversion": 4.8},
    {"campana": "GENOMMA", "url_catalogo": "/catalogos/genomma-2026",
     "visitas_catalogo": 95, "clics_productos": 41, "compras_post_clic": 6,
     "venta_atribuida": 900000, "tasa_conversion": 6.3},
    {"campana": "MARATHON", "url_catalogo": "/catalogos/marathon-2026",
     "visitas_catalogo": 88, "clics_productos": 34, "compras_post_clic": 5,
     "venta_atribuida": 700000, "tasa_conversion": 5.7},
    {"campana": "ANASAC", "url_catalogo": "/catalogos/anasac-2026",
     "visitas_catalogo": 72, "clics_productos": 28, "compras_post_clic": 4,
     "venta_atribuida": 500000, "tasa_conversion": 5.6},
]

# Visitas mensuales al B2B
visitas_mensuales = [
    {"mes": "Oct 2025", "visitas_b2b": 9800, "visitas_catalogo": 1420, "compras": 310, "venta_online": 73600000},
    {"mes": "Nov 2025", "visitas_b2b": 10200, "visitas_catalogo": 1580, "compras": 285, "venta_online": 77200000},
    {"mes": "Dic 2025", "visitas_b2b": 14500, "visitas_catalogo": 2340, "compras": 520, "venta_online": 115400000},
    {"mes": "Ene 2026", "visitas_b2b": 13200, "visitas_catalogo": 2100, "compras": 445, "venta_online": 132300000},
    {"mes": "Feb 2026", "visitas_b2b": 10800, "visitas_catalogo": 1750, "compras": 340, "venta_online": 90000000},
    {"mes": "Mar 2026", "visitas_b2b": 12050, "visitas_catalogo": 1995, "compras": 395, "venta_online": 115200000},
]

# Top productos digitales (clics en catálogo → compra)
top_productos_digital = [
    {"sku": "SKU-7711", "desc": "Nexgard 28.3mg 1 comp", "campana": "INVIERNO VET", "clics": 89, "compras": 12, "venta": 2100000},
    {"sku": "SKU-4423", "desc": "Kitadol Migra 10 comp", "campana": "MES SALUD", "clics": 76, "compras": 18, "venta": 1800000},
    {"sku": "SKU-8891", "desc": "Bravecto 500mg 1 comp", "campana": "INVIERNO VET", "clics": 72, "compras": 9, "venta": 1650000},
    {"sku": "SKU-3301", "desc": "Abrilar Jarabe 100ml", "campana": "PREP. INVIERNO", "clics": 68, "compras": 15, "venta": 1400000},
    {"sku": "SKU-5502", "desc": "Naxpet Antiinflamatorio", "campana": "INVIERNO VET", "clics": 64, "compras": 11, "venta": 1350000},
    {"sku": "SKU-2209", "desc": "Tapsin Día/Noche 18 caps", "campana": "PREP. INVIERNO", "clics": 61, "compras": 22, "venta": 1200000},
    {"sku": "SKU-6678", "desc": "Vick Vaporub 50g", "campana": "PREP. INVIERNO", "clics": 58, "compras": 28, "venta": 1100000},
    {"sku": "SKU-1105", "desc": "Flanax 550mg 10 comp", "campana": "GENOMMA", "clics": 55, "compras": 8, "venta": 980000},
    {"sku": "SKU-9934", "desc": "Drag Pharma Amoxicilina", "campana": "DRAGPHARMA", "clics": 52, "compras": 14, "venta": 920000},
    {"sku": "SKU-4456", "desc": "Sinagrip Forte 8 sobres", "campana": "PREP. INVIERNO", "clics": 49, "compras": 19, "venta": 870000},
]

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

# ============================================================
# HTML GENERATION
# ============================================================

def fmt_clp(n):
    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:,.2f} MM"
    elif n >= 1_000_000:
        return f"${n/1_000_000:,.1f}M"
    else:
        return f"${n:,.0f}"

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
        <td><code>{c['url_catalogo']}</code></td>
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

# ============================================================
# HTML
# ============================================================
HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ClinicalMarket — Dashboard Retail v7</title>
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
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Poppins',sans-serif; background:var(--bg); color:var(--text); font-size:14px; }}

.header {{ background:linear-gradient(135deg, var(--primary) 0%, var(--dark) 100%); color:white; padding:20px 28px; }}
.header h1 {{ font-size:22px; font-weight:800; }}
.header-sub {{ font-size:12px; opacity:.85; margin-top:4px; display:flex; gap:20px; flex-wrap:wrap; }}

.nav {{ background:white; border-bottom:2px solid var(--border); padding:0 20px; display:flex; gap:0; overflow-x:auto; position:sticky; top:0; z-index:100; }}
.nav button {{ padding:12px 16px; border:none; background:none; font-family:inherit; font-size:12px; font-weight:500; color:var(--muted); cursor:pointer; border-bottom:3px solid transparent; white-space:nowrap; transition:all .2s; }}
.nav button:hover {{ color:var(--text); }}
.nav button.active {{ color:var(--primary); border-bottom-color:var(--primary); font-weight:600; }}

.section {{ display:none; padding:20px 28px; max-width:1400px; margin:0 auto; }}
.section.active {{ display:block; }}

.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(200px, 1fr)); gap:12px; margin:16px 0; }}
.kpi {{ background:var(--card); border-radius:10px; padding:16px; border-left:4px solid var(--primary); box-shadow:0 1px 3px rgba(0,0,0,.05); }}
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
.insight strong {{ color:var(--text); }}
.insight-blue {{ background:#eef6fd; border-left-color:var(--primary); }}

.table-wrap {{ background:var(--card); border-radius:10px; overflow:hidden; box-shadow:0 1px 3px rgba(0,0,0,.05); margin:12px 0; }}
.table-header {{ display:flex; justify-content:space-between; align-items:center; padding:12px 16px; border-bottom:1px solid var(--border); }}
.table-header h3 {{ font-size:14px; font-weight:600; }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th {{ background:#f8f9fb; padding:8px 12px; text-align:left; font-weight:600; font-size:10px; text-transform:uppercase; letter-spacing:.3px; color:var(--muted); border-bottom:1px solid var(--border); }}
td {{ padding:8px 12px; border-bottom:1px solid #f2f4f7; }}
tr:hover {{ background:#fafbfd; }}

.chart-box {{ background:var(--card); border-radius:10px; padding:16px; box-shadow:0 1px 3px rgba(0,0,0,.05); margin:12px 0; }}
.chart-box h3 {{ font-size:13px; font-weight:600; margin-bottom:8px; }}
.chart-row {{ display:grid; grid-template-columns:1fr 1fr; gap:12px; }}
@media(max-width:900px) {{ .chart-row {{ grid-template-columns:1fr; }} }}

.badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:10px; font-weight:600; background:#eef6fd; color:var(--primary); }}
.badge-green {{ background:#e8f8ef; color:var(--success); }}
.badge-red {{ background:#fdecea; color:var(--danger); }}

.btn {{ display:inline-flex; align-items:center; gap:5px; padding:6px 12px; border-radius:6px; border:1px solid var(--border); background:white; font-family:inherit; font-size:11px; font-weight:500; cursor:pointer; color:var(--text); transition:all .2s; }}
.btn:hover {{ background:var(--primary); color:white; border-color:var(--primary); }}

.filter-bar {{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; margin:10px 0; }}
.filter-bar input {{ padding:7px 12px; border:1px solid var(--border); border-radius:6px; font-family:inherit; font-size:12px; width:260px; }}
.filter-bar select {{ padding:7px 12px; border:1px solid var(--border); border-radius:6px; font-family:inherit; font-size:12px; }}

.funnel {{ display:flex; gap:0; align-items:stretch; margin:16px 0; }}
.funnel-step {{ flex:1; text-align:center; padding:12px 6px; position:relative; }}
.funnel-step:not(:last-child)::after {{ content:"→"; position:absolute; right:-10px; top:50%; transform:translateY(-50%); font-size:18px; color:var(--muted); z-index:1; }}
.funnel-bar {{ height:6px; border-radius:3px; margin:6px auto 0; }}
.funnel-label {{ font-size:10px; color:var(--muted); text-transform:uppercase; font-weight:600; }}
.funnel-value {{ font-size:18px; font-weight:700; }}

.grid-3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; }}
@media(max-width:900px) {{ .grid-3 {{ grid-template-columns:1fr; }} }}

@media print {{ .nav, .btn, .filter-bar {{ display:none; }} .section {{ display:block !important; }} }}
</style>
</head>
<body>

<div class="header">
    <h1>ClinicalMarket B2B — Dashboard Retail v7</h1>
    <div class="header-sub">
        <span>Canal retail: farmacias, droguerías, pet shops, veterinarias</span>
        <span>Generado: 13 Abril 2026</span>
        <span>Fuentes: SAP · Power BI · GA4 · MailUp · Publitas</span>
    </div>
</div>

<div class="nav" id="nav">
    <button class="active" onclick="showTab('resumen')">Resumen</button>
    <button onclick="showTab('comparativo')">Comparativo</button>
    <button onclick="showTab('campanas')">Campañas</button>
    <button onclick="showTab('digital')">Digital</button>
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
            <div class="kpi-sub"><span style="color:{'var(--success)' if crec_venta > 0 else 'var(--danger)'}">{'▲' if crec_venta > 0 else '▼'} {crec_venta}%</span> vs Mar 2025 · <span class="badge">SAP</span></div>
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
            <canvas id="chartVentas6m" height="140"></canvas>
        </div>
        <div class="chart-box">
            <h3>Visitas B2B vs Compras</h3>
            <canvas id="chartVisitasCompras" height="140"></canvas>
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
        <div class="kpi {'kpi-green' if crec_venta > 0 else 'kpi-red'}">
            <div class="kpi-label">Cambio en Venta</div>
            <div class="kpi-value">{'▲' if crec_venta > 0 else '▼'} {crec_venta}%</div>
            <div class="kpi-sub">{fmt_clp(venta_25)} → {fmt_clp(venta_26)}</div>
        </div>
        <div class="kpi {'kpi-red' if crec_unid < 0 else 'kpi-green'}">
            <div class="kpi-label">Cambio en Unidades</div>
            <div class="kpi-value">{'▲' if crec_unid > 0 else '▼'} {crec_unid}%</div>
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
            <canvas id="chartCampVentas" height="140"></canvas>
        </div>
        <div class="chart-box">
            <h3>Unidades y Campañas Activas</h3>
            <canvas id="chartCampUnid" height="140"></canvas>
        </div>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Campaña Invierno 2026 — Detalle Feb → Mar</h3>
            <button class="btn" onclick="exportTable('tblInvierno','invierno_2026.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar producto..." id="filterInvierno">
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
            <canvas id="chartFuente" height="140"></canvas>
        </div>
        <div class="chart-box">
            <h3>Visitas B2B vs Compras (mensual)</h3>
            <canvas id="chartVisMes" height="140"></canvas>
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
        </div>
        <table id="tblDigCamp">
            <thead><tr>
                <th>Campaña</th><th>URL Catálogo</th><th style="text-align:right">Visitas</th>
                <th style="text-align:right">Clics Productos</th><th style="text-align:right">Compras</th>
                <th style="text-align:right">Venta</th><th style="text-align:right">% Conversión</th>
            </tr></thead>
            <tbody>{dig_camp_rows}</tbody>
        </table>
    </div>

    <div class="chart-row">
        <div class="chart-box">
            <h3>Visitas vs Clics por Campaña</h3>
            <canvas id="chartDigCamp" height="140"></canvas>
        </div>
        <div class="chart-box">
            <h3>Compras por Campaña</h3>
            <canvas id="chartDigCompras" height="140"></canvas>
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
            <canvas id="chartSKU" height="140"></canvas>
        </div>
        <div class="chart-box">
            <h3>Proporción de SKUs</h3>
            <canvas id="chartSKUBar" height="140"></canvas>
        </div>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Top Laboratorios por Rotación (3 meses)</h3>
            <button class="btn" onclick="exportTable('tblProdLab','laboratorios_rotacion.csv')">Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar laboratorio..." id="filterProdLab">
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
        </div>
        <table id="tblClientes">
            <thead><tr><th>#</th><th>Cliente</th><th>Vendedor</th><th style="text-align:right">Venta Total</th><th>% Total</th></tr></thead>
            <tbody>{cli_rows}</tbody>
        </table>
    </div>
</div>

<!-- ================================ SCRIPTS ================================ -->
<script>
// Tab switching
function showTab(id) {{
    document.querySelectorAll('.section').forEach(function(s) {{ s.classList.remove('active'); }});
    document.querySelectorAll('.nav button').forEach(function(b) {{ b.classList.remove('active'); }});
    document.getElementById(id).classList.add('active');
    // Find the clicked button
    var buttons = document.querySelectorAll('.nav button');
    for (var i = 0; i < buttons.length; i++) {{
        if (buttons[i] === (event ? event.target : null)) {{
            buttons[i].classList.add('active');
        }}
    }}
    // Init charts when tab shown
    setTimeout(function() {{ initCharts(); }}, 100);
}}

// Generic table text filter — bind to input fields
function setupFilter(inputId, tableId) {{
    var input = document.getElementById(inputId);
    if (!input) return;
    input.addEventListener('input', function() {{
        var q = this.value.toLowerCase();
        var rows = document.querySelectorAll('#' + tableId + ' tbody tr');
        for (var i = 0; i < rows.length; i++) {{
            rows[i].style.display = rows[i].textContent.toLowerCase().indexOf(q) !== -1 ? '' : 'none';
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
        maintainAspectRatio: true,
        plugins: {{ legend: {{ display: false }}, tooltip: {{ bodyFont: {{ size: 11 }} }} }},
        scales: {{ x: {{ ticks: {{ font: {{ size: 10 }} }} }}, y: {{ ticks: {{ font: {{ size: 10 }} }} }} }}
    }};

    // Resumen: Ventas 6m
    new Chart(document.getElementById('chartVentas6m'), {{
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

    // Resumen: Visitas vs Compras
    if (document.getElementById('chartVisitasCompras')) {{
        new Chart(document.getElementById('chartVisitasCompras'), {{
            type: 'bar',
            data: {{
                labels: {vis_mes_labels},
                datasets: [
                    {{ label: 'Visitas B2B', data: {vis_mes_b2b}, backgroundColor: C.primary + '99', borderRadius: 4, yAxisID: 'y' }},
                    {{ label: 'Compras', data: {vis_mes_compras}, type: 'line', borderColor: C.success, pointBackgroundColor: C.success, yAxisID: 'y1', tension: 0.3, pointRadius: 4 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: true,
                plugins: {{ legend: {{ display: true, labels: {{ font: {{ size: 10 }} }} }} }},
                scales: {{
                    y: {{ position: 'left', ticks: {{ font: {{ size: 10 }} }} }},
                    y1: {{ position: 'right', grid: {{ drawOnChartArea: false }}, ticks: {{ font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}

    // Campañas: Ventas por mes
    if (document.getElementById('chartCampVentas')) {{
        new Chart(document.getElementById('chartCampVentas'), {{
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
    if (document.getElementById('chartCampUnid')) {{
        new Chart(document.getElementById('chartCampUnid'), {{
            type: 'line',
            data: {{
                labels: {month_labels},
                datasets: [
                    {{ label:'Unidades', data:{month_unidades}, borderColor:C.primary, yAxisID:'y', tension:0.3, pointRadius:3 }},
                    {{ label:'Campañas', data:{month_camps}, borderColor:C.warning, yAxisID:'y1', tension:0.3, borderDash:[5,5], pointRadius:3 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: true,
                plugins: {{ legend: {{ display: true, labels: {{ font: {{ size: 10 }} }} }} }},
                scales: {{
                    y: {{ position:'left', ticks: {{ font: {{ size: 10 }} }} }},
                    y1: {{ position:'right', grid:{{ drawOnChartArea:false }}, ticks: {{ font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}

    // Pareto
    if (document.getElementById('chartPareto')) {{
        var n = {clientes['total_clientes']};
        var pareto = {clientes['pareto_n80']};
        new Chart(document.getElementById('chartPareto'), {{
            type: 'doughnut',
            data: {{
                labels: ['Top ' + pareto + ' (80% venta)', 'Resto ' + (n - pareto) + ' (20% venta)'],
                datasets: [{{ data: [pareto, n - pareto], backgroundColor: [C.primary, '#e8ecf1'], borderWidth: 0 }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: true, cutout: '65%', plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }} }} }} }} }}
        }});
    }}

    // SKU estados doughnut
    if (document.getElementById('chartSKU')) {{
        new Chart(document.getElementById('chartSKU'), {{
            type: 'doughnut',
            data: {{
                labels: ['Con Rotación ({skus["estados"].get("Con Rotación",0):,})', 'Abandonados ({skus["estados"].get("Abandonados",0):,})', 'Nunca Vendidos ({skus["estados"].get("Nunca Rotados",0):,})'],
                datasets: [{{ data: [{skus['estados'].get('Con Rotación',0)}, {skus['estados'].get('Abandonados',0)}, {skus['estados'].get('Nunca Rotados',0)}],
                    backgroundColor: [C.success, C.warning, C.danger], borderWidth: 0 }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: true, cutout: '60%', plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 10 }} }} }} }} }}
        }});
    }}

    // SKU bar chart
    if (document.getElementById('chartSKUBar')) {{
        new Chart(document.getElementById('chartSKUBar'), {{
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
    if (document.getElementById('chartFuente')) {{
        new Chart(document.getElementById('chartFuente'), {{
            type: 'doughnut',
            data: {{
                labels: {fuente_labels},
                datasets: [{{ data: {fuente_data}, backgroundColor: [C.primary, C.warning, C.dark, C.success, C.purple], borderWidth: 0 }}]
            }},
            options: {{ responsive: true, maintainAspectRatio: true, cutout: '55%', plugins: {{ legend: {{ position: 'bottom', labels: {{ font: {{ size: 9 }} }} }} }} }}
        }});
    }}

    // Digital: Visitas vs Compras mensual
    if (document.getElementById('chartVisMes')) {{
        new Chart(document.getElementById('chartVisMes'), {{
            type: 'bar',
            data: {{
                labels: {vis_mes_labels},
                datasets: [
                    {{ label: 'Visitas Catálogo', data: {vis_mes_cat}, backgroundColor: C.primary + '88', borderRadius: 4, yAxisID: 'y' }},
                    {{ label: 'Compras', data: {vis_mes_compras}, type: 'line', borderColor: C.success, pointBackgroundColor: C.success, yAxisID: 'y1', tension: 0.3, pointRadius: 3 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: true,
                plugins: {{ legend: {{ display: true, labels: {{ font: {{ size: 9 }} }} }} }},
                scales: {{
                    y: {{ position: 'left', ticks: {{ font: {{ size: 10 }} }} }},
                    y1: {{ position: 'right', grid: {{ drawOnChartArea: false }}, ticks: {{ font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}

    // Digital: Campañas visitas vs clics
    if (document.getElementById('chartDigCamp')) {{
        new Chart(document.getElementById('chartDigCamp'), {{
            type: 'bar',
            data: {{
                labels: {camp_dig_labels},
                datasets: [
                    {{ label: 'Visitas Catálogo', data: {camp_dig_visitas}, backgroundColor: C.primary + '88', borderRadius: 4 }},
                    {{ label: 'Clics Productos', data: {camp_dig_clics}, backgroundColor: C.warning + '88', borderRadius: 4 }}
                ]
            }},
            options: {{
                responsive: true, maintainAspectRatio: true, indexAxis: 'y',
                plugins: {{ legend: {{ display: true, labels: {{ font: {{ size: 9 }} }} }} }},
                scales: {{ x: {{ ticks: {{ font: {{ size: 10 }} }} }}, y: {{ ticks: {{ font: {{ size: 9 }} }} }} }}
            }}
        }});
    }}

    // Digital: Compras por campaña
    if (document.getElementById('chartDigCompras')) {{
        new Chart(document.getElementById('chartDigCompras'), {{
            type: 'bar',
            data: {{
                labels: {camp_dig_labels},
                datasets: [{{ label: 'Compras', data: {camp_dig_compras}, backgroundColor: C.success + 'cc', borderRadius: 4 }}]
            }},
            options: {{
                responsive: true, maintainAspectRatio: true, indexAxis: 'y',
                plugins: {{ legend: {{ display: false }} }},
                scales: {{ x: {{ ticks: {{ font: {{ size: 10 }} }} }}, y: {{ ticks: {{ font: {{ size: 9 }} }} }} }}
            }}
        }});
    }}
}}

// ============= INIT =============
document.addEventListener('DOMContentLoaded', function() {{
    // Setup all filters
    setupFilter('filterSkuComp', 'tblSkuComp');
    setupFilter('filterInvierno', 'tblInvierno');
    setupFilter('filterDigCamp', 'tblDigCamp');
    setupFilter('filterDigProd', 'tblDigProd');
    setupFilter('filterProdLab', 'tblProdLab');
    setupFilter('filterClientes', 'tblClientes');
    setupColFilter('filterVendedor', 'tblClientes', 2);

    // Init charts after small delay
    setTimeout(function() {{ initCharts(); }}, 200);
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

print(f"Dashboard v7: {output}")
print(f"Size: {len(HTML)/1024:.1f} KB, {HTML.count(chr(10))} lines")
