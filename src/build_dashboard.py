#!/usr/bin/env python3
"""ClinicalMarket Dashboard v6 — Canal RETAIL
Super simple, con filtros, exportables, comparativas y oportunidades.
Sin Roadmap. GA4 arreglado. Para gente que NO entiende datos."""

import json, os, textwrap

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# When run from repo: data is at ../data relative to src/
# When run standalone: data is in same dir or in ecommerce-b2b/data
DATA_PATHS = [
    os.path.join(SCRIPT_DIR, 'mnt/Clinical Dev - ClinicalMarket, Gesmed y Profar/ecommerce-b2b/data'),
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

# Mailing data (hardcoded for now)
mailing = {
    "ultima_campana": "Catálogos Abril 2026",
    "enviados": 3100, "aperturas": 672, "tasa_apertura": 23.26,
    "clics": 115, "tasa_clic": 3.98, "sesiones_email": 2859
}

# Campaign months (from PDFs — hardcoded)
meses = [
    {"mes": "Oct 2025", "campanas": 14, "unidades": 45195, "ventas": 73600000},
    {"mes": "Nov 2025", "campanas": 13, "unidades": 27463, "ventas": 77200000},
    {"mes": "Dic 2025", "campanas": 14, "unidades": 107457, "ventas": 115400000},
    {"mes": "Ene 2026", "campanas": 15, "unidades": 58702, "ventas": 132300000},
    {"mes": "Feb 2026", "campanas": 12, "unidades": 36487, "ventas": 90000000},
    {"mes": "Mar 2026", "campanas": 8,  "unidades": 40443, "ventas": 115200000},
]

# GA4 data (simplified)
ga4 = {
    "bounce_rate": 42.3,
    "sesiones_email": 2859,
    "eventos_publitas": 3,
    "top_landings": [
        {"path": "/", "vistas": 8420, "bounce": 38.1},
        {"path": "/catalogos", "vistas": 3215, "bounce": 29.5},
        {"path": "/producto/*", "vistas": 2890, "bounce": 51.2},
        {"path": "/registro", "vistas": 1240, "bounce": 62.8},
        {"path": "/carrito", "vistas": 890, "bounce": 44.3},
    ]
}

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

# Best month
best_month = max(meses, key=lambda x: x['ventas'])

# Campañas que más crecieron
camp_crecimiento = [c for c in comp['campanas'] if c['venta_26'] > 0 and c['nombre'] != 'SIN CAMPAÑA']
camp_crecimiento.sort(key=lambda x: x['venta_26'], reverse=True)

# ============================================================
# HTML GENERATION
# ============================================================

def fmt_clp(n):
    """Format CLP to readable string"""
    if n >= 1_000_000_000:
        return f"${n/1_000_000_000:,.2f} MM"
    elif n >= 1_000_000:
        return f"${n/1_000_000:,.1f}M"
    else:
        return f"${n:,.0f}"

def fmt_pct(n):
    return f"{n:+.1f}%" if n else "—"

# Generate campaign rows
camp_rows_html = ""
for c in comp['campanas']:
    if c['nombre'] == 'SIN CAMPAÑA': continue
    delta = c['venta_26'] - c['venta_25']
    arrow = "▲" if delta > 0 else "▼" if delta < 0 else "→"
    color = "#27ae60" if delta > 0 else "#e74c3c" if delta < 0 else "#95a5a6"
    camp_rows_html += f"""<tr>
        <td><strong>{c['nombre']}</strong></td>
        <td>{c['skus']}</td>
        <td>{fmt_clp(c['venta_25'])}</td>
        <td>{fmt_clp(c['venta_26'])}</td>
        <td style="color:{color};font-weight:700">{arrow} {fmt_clp(abs(delta))}</td>
        <td><span style="color:#27ae60">+{c['grew']}</span> | <span style="color:#0DA7EE">{c['new']} nuevos</span> | <span style="color:#e74c3c">{c['dropped']} caídos</span></td>
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

# Vendedores rows
vend_rows = ""
for v in clientes['vendedores']:
    pct = round(v['venta'] / clientes['total_venta'] * 100, 1)
    vend_rows += f"""<tr>
        <td><strong>{v['nombre']}</strong></td>
        <td>{v['clientes']}</td>
        <td style="text-align:right;font-weight:600">{fmt_clp(v['venta'])}</td>
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

# Month chart data
month_labels = json.dumps([m['mes'] for m in meses])
month_ventas = json.dumps([round(m['ventas']/1_000_000) for m in meses])
month_unidades = json.dumps([m['unidades'] for m in meses])
month_camps = json.dumps([m['campanas'] for m in meses])

# Lab chart data
top_labs = skus['top_laboratorios'][:10]
lab_names = json.dumps([l['nombre'][:20] for l in top_labs])
lab_rot = json.dumps([l['rotacion_3m'] for l in top_labs])
lab_skus_data = json.dumps([l['skus'] for l in top_labs])

# Landing data
landing_rows = ""
for l in ga4['top_landings']:
    diag = "Excelente" if l['bounce'] < 35 else "Bueno" if l['bounce'] < 45 else "Mejorar" if l['bounce'] < 55 else "Revisar"
    color = "#27ae60" if l['bounce'] < 35 else "#f39c12" if l['bounce'] < 50 else "#e74c3c"
    landing_rows += f"""<tr>
        <td><code>{l['path']}</code></td>
        <td style="text-align:right">{l['vistas']:,}</td>
        <td style="text-align:right">{l['bounce']}%</td>
        <td style="color:{color};font-weight:600">{diag}</td>
    </tr>"""

HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ClinicalMarket — Dashboard Retail v6</title>
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

/* HEADER */
.header {{ background:linear-gradient(135deg, var(--primary) 0%, var(--dark) 100%); color:white; padding:24px 32px; }}
.header h1 {{ font-size:26px; font-weight:800; }}
.header-sub {{ font-size:13px; opacity:.85; margin-top:4px; display:flex; gap:24px; flex-wrap:wrap; }}

/* NAV TABS */
.nav {{ background:white; border-bottom:2px solid var(--border); padding:0 24px; display:flex; gap:0; overflow-x:auto; position:sticky; top:0; z-index:100; }}
.nav button {{ padding:14px 20px; border:none; background:none; font-family:inherit; font-size:13px; font-weight:500; color:var(--muted); cursor:pointer; border-bottom:3px solid transparent; white-space:nowrap; transition:all .2s; }}
.nav button:hover {{ color:var(--text); }}
.nav button.active {{ color:var(--primary); border-bottom-color:var(--primary); font-weight:600; }}

/* SECTIONS */
.section {{ display:none; padding:24px 32px; max-width:1400px; margin:0 auto; }}
.section.active {{ display:block; }}

/* CARDS */
.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:16px; margin:20px 0; }}
.kpi {{ background:var(--card); border-radius:12px; padding:20px; border-left:4px solid var(--primary); box-shadow:0 1px 4px rgba(0,0,0,.06); }}
.kpi-label {{ font-size:11px; text-transform:uppercase; letter-spacing:.5px; color:var(--muted); font-weight:600; }}
.kpi-value {{ font-size:28px; font-weight:800; color:var(--dark); margin:6px 0 4px; }}
.kpi-sub {{ font-size:12px; color:var(--muted); }}
.kpi-green {{ border-left-color:var(--success); }}
.kpi-green .kpi-value {{ color:var(--success); }}
.kpi-orange {{ border-left-color:var(--warning); }}
.kpi-orange .kpi-value {{ color:var(--warning); }}
.kpi-red {{ border-left-color:var(--danger); }}
.kpi-red .kpi-value {{ color:var(--danger); }}

/* INSIGHT BOX */
.insight {{ background:#fffbeb; border-left:4px solid var(--warning); padding:16px 20px; border-radius:8px; margin:16px 0; font-size:13px; line-height:1.6; }}
.insight strong {{ color:var(--text); }}
.insight-blue {{ background:#eef6fd; border-left-color:var(--primary); }}

/* TABLES */
.table-wrap {{ background:var(--card); border-radius:12px; overflow:hidden; box-shadow:0 1px 4px rgba(0,0,0,.06); margin:16px 0; }}
.table-header {{ display:flex; justify-content:space-between; align-items:center; padding:16px 20px; border-bottom:1px solid var(--border); }}
.table-header h3 {{ font-size:15px; font-weight:600; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
th {{ background:#f8f9fb; padding:10px 14px; text-align:left; font-weight:600; font-size:11px; text-transform:uppercase; letter-spacing:.3px; color:var(--muted); border-bottom:1px solid var(--border); }}
td {{ padding:10px 14px; border-bottom:1px solid #f2f4f7; }}
tr:hover {{ background:#fafbfd; }}

/* CHART CONTAINER */
.chart-box {{ background:var(--card); border-radius:12px; padding:20px; box-shadow:0 1px 4px rgba(0,0,0,.06); margin:16px 0; }}
.chart-box h3 {{ font-size:15px; font-weight:600; margin-bottom:12px; }}
.chart-row {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
@media(max-width:900px) {{ .chart-row {{ grid-template-columns:1fr; }} }}

/* BADGE */
.badge {{ display:inline-block; padding:2px 8px; border-radius:10px; font-size:11px; font-weight:600; background:#eef6fd; color:var(--primary); }}
.badge-green {{ background:#e8f8ef; color:var(--success); }}
.badge-red {{ background:#fdecea; color:var(--danger); }}

/* BUTTONS */
.btn {{ display:inline-flex; align-items:center; gap:6px; padding:8px 16px; border-radius:8px; border:1px solid var(--border); background:white; font-family:inherit; font-size:12px; font-weight:500; cursor:pointer; color:var(--text); transition:all .2s; }}
.btn:hover {{ background:var(--primary); color:white; border-color:var(--primary); }}
.btn-sm {{ padding:5px 10px; font-size:11px; }}

/* FILTER BAR */
.filter-bar {{ display:flex; gap:12px; align-items:center; flex-wrap:wrap; margin:12px 0; }}
.filter-bar input {{ padding:8px 14px; border:1px solid var(--border); border-radius:8px; font-family:inherit; font-size:13px; width:280px; }}
.filter-bar select {{ padding:8px 14px; border:1px solid var(--border); border-radius:8px; font-family:inherit; font-size:13px; }}

/* FUNNEL */
.funnel {{ display:flex; gap:0; align-items:stretch; margin:20px 0; }}
.funnel-step {{ flex:1; text-align:center; padding:16px 8px; position:relative; }}
.funnel-step:not(:last-child)::after {{ content:"→"; position:absolute; right:-12px; top:50%; transform:translateY(-50%); font-size:20px; color:var(--muted); z-index:1; }}
.funnel-bar {{ height:8px; border-radius:4px; margin:8px auto 0; }}
.funnel-label {{ font-size:11px; color:var(--muted); text-transform:uppercase; font-weight:600; }}
.funnel-value {{ font-size:22px; font-weight:700; }}

/* Print */
@media print {{ .nav, .btn, .filter-bar {{ display:none; }} .section {{ display:block !important; }} }}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
    <h1>ClinicalMarket B2B — Dashboard Retail v6</h1>
    <div class="header-sub">
        <span>Solo canal retail (farmacias, droguerías, pet shops, veterinarias)</span>
        <span>Generado: 13-Abril-2026</span>
        <span>Fuentes: SAP · Power BI · GA4 · MailUp</span>
        <span><a href="https://github.com/Roda-code/ecommerce-b2b" style="color:white">GitHub</a></span>
    </div>
</div>

<!-- NAV -->
<div class="nav" id="nav">
    <button class="active" onclick="showTab('resumen')">📊 Resumen</button>
    <button onclick="showTab('comparativo')">📈 Comparativo</button>
    <button onclick="showTab('campanas')">🎯 Campañas</button>
    <button onclick="showTab('clientes')">👥 Clientes</button>
    <button onclick="showTab('vendedores')">💼 Vendedores</button>
    <button onclick="showTab('productos')">📦 Productos</button>
    <button onclick="showTab('digital')">🌐 Digital</button>
    <button onclick="showTab('laboratorios')">🏭 Laboratorios</button>
</div>

<!-- ================================ RESUMEN ================================ -->
<div class="section active" id="resumen">
    <div class="insight">
        <strong>¿Cómo leer este dashboard?</strong> Muestra el rendimiento de ventas del canal retail de ClinicalMarket B2B.
        Los datos vienen de SAP (ventas reales), Power BI (campañas), GA4 (tráfico web) y MailUp (emails).
        Cada número tiene una etiqueta que indica su fuente. Usa las pestañas arriba para navegar.
    </div>

    <h2 style="margin:20px 0 8px">Métricas clave — Marzo 2026 vs 2025</h2>
    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Venta Marzo 2026</div>
            <div class="kpi-value">{fmt_clp(venta_26)}</div>
            <div class="kpi-sub"><span style="color:{'var(--success)' if crec_venta > 0 else 'var(--danger)'}">{'▲' if crec_venta > 0 else '▼'} {crec_venta}%</span> vs Mar 2025 · <span class="badge">SAP</span></div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">Margen Bruto</div>
            <div class="kpi-value">{margen_26}%</div>
            <div class="kpi-sub">+5.6% vs año anterior · <span class="badge badge-green">SAP</span></div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Venta Acumulada Retail</div>
            <div class="kpi-value">{fmt_clp(clientes['total_venta'])}</div>
            <div class="kpi-sub">{clientes['total_clientes']} clientes retail · 2025-2026 · <span class="badge">SAP</span></div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Campañas activas (6 meses)</div>
            <div class="kpi-value">{sum(m['campanas'] for m in meses)}</div>
            <div class="kpi-sub">{total_unid_6m:,} unidades · {fmt_clp(total_ventas_6m)} · <span class="badge">PB</span></div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi kpi-orange">
            <div class="kpi-label">Clientes Pareto (80% venta)</div>
            <div class="kpi-value">Top {clientes['pareto_n80']}</div>
            <div class="kpi-sub">{clientes['pareto_pct']}% de la base genera el 80% del ingreso</div>
        </div>
        <div class="kpi kpi-red">
            <div class="kpi-label">Productos sin rotación</div>
            <div class="kpi-value">{skus['estados'].get('Nunca Rotados', 0):,}</div>
            <div class="kpi-sub">de {skus['total_skus']:,} SKUs totales · nunca vendidos</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Mailing — Tasa apertura</div>
            <div class="kpi-value">{mailing['tasa_apertura']}%</div>
            <div class="kpi-sub">{mailing['clics']} clics · {mailing['enviados']:,} envíos · <span class="badge">MU</span></div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Bounce Rate Web</div>
            <div class="kpi-value">{ga4['bounce_rate']}%</div>
            <div class="kpi-sub">Benchmark B2B: 40-55% · <span class="badge">GA4</span></div>
        </div>
    </div>

    <div class="chart-row">
        <div class="chart-box">
            <h3>Evolución de Ventas Campañas (6 meses)</h3>
            <canvas id="chartVentas6m" height="200"></canvas>
        </div>
        <div class="chart-box">
            <h3>Unidades vendidas por mes</h3>
            <canvas id="chartUnidades6m" height="200"></canvas>
        </div>
    </div>

    <div class="insight-blue insight" style="margin-top:20px">
        <strong>Oportunidades detectadas:</strong><br>
        1. <strong>Concentración de clientes:</strong> {clientes['pareto_pct']}% de los clientes genera el 80% — hay {clientes['total_clientes'] - clientes['pareto_n80']} clientes con potencial de crecimiento.<br>
        2. <strong>Catálogo sin mover:</strong> {skus['estados'].get('Nunca Rotados', 0):,} SKUs nunca se han vendido — oportunidad de depuración o activación.<br>
        3. <strong>Campañas Invierno:</strong> Prep. Invierno generó {fmt_clp(camp_crecimiento[0]['venta_26'] if camp_crecimiento else 0)} con {camp_crecimiento[0]['grew'] if camp_crecimiento else 0} SKUs en crecimiento.<br>
        4. <strong>Margen mejorando:</strong> Subió de 11.1% a {margen_26}% año contra año — la mezcla de productos está mejorando.
    </div>
</div>

<!-- ================================ COMPARATIVO ================================ -->
<div class="section" id="comparativo">
    <h2>Comparativo Marzo 2025 vs Marzo 2026</h2>
    <div class="insight">Compara el mismo mes del año anterior para ver crecimiento real, sin estacionalidad. Los datos vienen de SAP vía Power BI.</div>

    <div class="kpi-grid">
        <div class="kpi {'kpi-green' if crec_venta > 0 else 'kpi-red'}">
            <div class="kpi-label">Δ Venta</div>
            <div class="kpi-value">{'▲' if crec_venta > 0 else '▼'} {crec_venta}%</div>
            <div class="kpi-sub">{fmt_clp(venta_25)} → {fmt_clp(venta_26)}</div>
        </div>
        <div class="kpi {'kpi-red' if crec_unid < 0 else 'kpi-green'}">
            <div class="kpi-label">Δ Unidades</div>
            <div class="kpi-value">{'▲' if crec_unid > 0 else '▼'} {crec_unid}%</div>
            <div class="kpi-sub">{unid_25:,} → {unid_26:,}</div>
        </div>
        <div class="kpi kpi-green">
            <div class="kpi-label">Δ Margen</div>
            <div class="kpi-value">▲ +5.7%</div>
            <div class="kpi-sub">11.1% → {margen_26}% sobre venta</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Campañas Activas Mar 2026</div>
            <div class="kpi-value">8</div>
            <div class="kpi-sub">vs 0 campañas especiales Mar 2025</div>
        </div>
    </div>

    <div class="insight-blue insight">
        <strong>Lectura rápida:</strong> La venta se mantuvo estable (+0.1%) pero con menos unidades (-4.6%), lo que significa que
        el <strong>ticket promedio subió</strong>. El margen bruto mejoró +5.7%, señal de que se están vendiendo productos de mayor valor.
        Las campañas nuevas (Prep. Invierno, Invierno Vet, Dragpharma) compensaron la caída natural del catálogo sin campaña.
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Rendimiento por Campaña — Marzo 2025 vs 2026</h3>
            <button class="btn btn-sm" onclick="exportTable('tblCampComp','campanas_comparativo.csv')">⬇ Exportar CSV</button>
        </div>
        <table id="tblCampComp">
            <thead><tr><th>Campaña</th><th>SKUs</th><th>Venta 2025</th><th>Venta 2026</th><th>Δ Venta</th><th>Movimiento SKUs</th></tr></thead>
            <tbody>{camp_rows_html}</tbody>
        </table>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Top 20 SKUs por Venta — Marzo 2026</h3>
            <button class="btn btn-sm" onclick="exportTable('tblSkuComp','skus_comparativo.csv')">⬇ Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar SKU o descripción..." oninput="filterTable('tblSkuComp', this.value)">
        </div>
        <table id="tblSkuComp">
            <thead><tr><th>SKU</th><th>Descripción</th><th>Campaña</th><th>Venta 2025</th><th>Venta 2026</th><th>Crec.</th></tr></thead>
            <tbody>{sku_comp_rows}</tbody>
        </table>
    </div>
</div>

<!-- ================================ CAMPAÑAS ================================ -->
<div class="section" id="campanas">
    <h2>Campañas — Evolución Mensual</h2>
    <div class="insight">Seguimiento mes a mes de las campañas activas en el ecommerce B2B. Datos de Power BI.</div>

    <div class="chart-row">
        <div class="chart-box">
            <h3>Ventas por Campaña ($M)</h3>
            <canvas id="chartCampVentas" height="220"></canvas>
        </div>
        <div class="chart-box">
            <h3>Campañas activas y Unidades</h3>
            <canvas id="chartCampUnid" height="220"></canvas>
        </div>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Detalle Campaña Invierno 2026 (Feb → Mar)</h3>
            <button class="btn btn-sm" onclick="exportTable('tblInvierno','invierno_2026.csv')">⬇ Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar producto..." oninput="filterTable('tblInvierno', this.value)">
        </div>
        <table id="tblInvierno">
            <thead><tr><th>SKU</th><th>Producto</th><th>Segmento</th><th>Venta Feb</th><th>Venta Mar</th><th>Crec. Feb→Mar</th></tr></thead>
            <tbody>{inv_rows}</tbody>
        </table>
    </div>

    <div class="insight-blue insight">
        <strong>Mejores rendimientos campañas:</strong> Prep. Invierno lidera con 121 SKUs y {fmt_clp(camp_crecimiento[0]['venta_26'] if camp_crecimiento else 0)}.
        Invierno Vet en segundo lugar con productos veterinarios creciendo fuerte (Nexgard, Bravecto, Naxpet).
    </div>
</div>

<!-- ================================ CLIENTES ================================ -->
<div class="section" id="clientes">
    <h2>Clientes Retail — Base CDP</h2>
    <div class="insight">Base completa de clientes retail con compras 2025-2026. Filtrado desde SAP: solo Ecommerce B2B + Retail + Retail Zona Extrema.</div>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Total Clientes Retail</div>
            <div class="kpi-value">{clientes['total_clientes']}</div>
            <div class="kpi-sub">Con compra en 2025-2026</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Venta Total Retail</div>
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
        <h3>Distribución Pareto — Concentración de Venta</h3>
        <canvas id="chartPareto" height="180"></canvas>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Top 30 Clientes Retail</h3>
            <button class="btn btn-sm" onclick="exportTable('tblClientes','clientes_retail.csv')">⬇ Exportar CSV</button>
        </div>
        <div class="filter-bar">
            <input type="text" placeholder="Buscar cliente o vendedor..." oninput="filterTable('tblClientes', this.value)">
            <select onchange="filterTableCol('tblClientes', 2, this.value)">
                <option value="">Todos los vendedores</option>
                {''.join(f'<option value="{v["nombre"]}">{v["nombre"]}</option>' for v in clientes['vendedores'])}
            </select>
        </div>
        <table id="tblClientes">
            <thead><tr><th>#</th><th>Cliente</th><th>Vendedor</th><th style="text-align:right">Venta Total</th><th>% del Total</th></tr></thead>
            <tbody>{cli_rows}</tbody>
        </table>
    </div>
</div>

<!-- ================================ VENDEDORES ================================ -->
<div class="section" id="vendedores">
    <h2>Vendedores — Rendimiento Retail</h2>
    <div class="insight">Venta acumulada 2025-2026 por vendedor, solo canal retail.</div>

    <div class="chart-box">
        <h3>Venta por Vendedor ($M)</h3>
        <canvas id="chartVendedores" height="260"></canvas>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Detalle por Vendedor</h3>
            <button class="btn btn-sm" onclick="exportTable('tblVendedores','vendedores.csv')">⬇ Exportar CSV</button>
        </div>
        <table id="tblVendedores">
            <thead><tr><th>Vendedor</th><th>Clientes</th><th style="text-align:right">Venta</th><th>% Total</th></tr></thead>
            <tbody>{vend_rows}</tbody>
        </table>
    </div>
</div>

<!-- ================================ PRODUCTOS ================================ -->
<div class="section" id="productos">
    <h2>Productos — Estado del Catálogo</h2>
    <div class="insight">Vista del catálogo completo del ecommerce: {skus['total_skus']:,} SKUs. Incluye rotación, abandonos y quiebres de stock.</div>

    <div class="kpi-grid">
        <div class="kpi kpi-green">
            <div class="kpi-label">Con Rotación</div>
            <div class="kpi-value">{skus['estados'].get('Con Rotación', 0):,}</div>
            <div class="kpi-sub">SKUs con ventas en últimos 3 meses</div>
        </div>
        <div class="kpi kpi-orange">
            <div class="kpi-label">Abandonados</div>
            <div class="kpi-value">{skus['estados'].get('Abandonados', 0):,}</div>
            <div class="kpi-sub">Antes vendían, ahora no</div>
        </div>
        <div class="kpi kpi-red">
            <div class="kpi-label">Nunca Vendidos</div>
            <div class="kpi-value">{skus['estados'].get('Nunca Rotados', 0):,}</div>
            <div class="kpi-sub">Sin una sola venta en 12 meses</div>
        </div>
        <div class="kpi kpi-red">
            <div class="kpi-label">Quiebres de Stock</div>
            <div class="kpi-value">{skus['quiebres_stock']:,}</div>
            <div class="kpi-sub">SKUs con stock agotado</div>
        </div>
    </div>

    <div class="chart-box">
        <h3>Distribución del Catálogo</h3>
        <canvas id="chartSKU" height="180"></canvas>
    </div>

    <div class="insight-blue insight">
        <strong>Oportunidad de limpieza:</strong> {skus['estados'].get('Nunca Rotados', 0):,} SKUs ({round(skus['estados'].get('Nunca Rotados', 0)/skus['total_skus']*100)}% del catálogo) nunca se han vendido.
        Depurar estos productos mejoraría la experiencia de búsqueda para los clientes y reduciría ruido en campañas.
        Los {skus['estados'].get('Abandonados', 0):,} abandonados son candidatos a reactivación con campaña especial.
    </div>
</div>

<!-- ================================ DIGITAL ================================ -->
<div class="section" id="digital">
    <h2>Digital — Tráfico y Comportamiento Web</h2>
    <div class="insight">GA4 mide el <strong>tráfico y comportamiento</strong> en clinicalmarket.cl — NO las ventas (B2B compra mayoritariamente offline).
    Lo usamos para entender cuánta gente llega, desde dónde, y qué tan bien funciona cada página.</div>

    <h3 style="margin:20px 0 12px">El embudo digital</h3>
    <div class="funnel">
        <div class="funnel-step">
            <div class="funnel-label">Visitas totales</div>
            <div class="funnel-value" style="color:var(--primary)">8,420</div>
            <div class="funnel-bar" style="width:100%;background:var(--primary)"></div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">Usuarios que llegan al sitio</div>
        </div>
        <div class="funnel-step">
            <div class="funnel-label">Ven catálogo</div>
            <div class="funnel-value" style="color:var(--dark)">3,215</div>
            <div class="funnel-bar" style="width:38%;background:var(--dark)"></div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">38% navega productos</div>
        </div>
        <div class="funnel-step">
            <div class="funnel-label">Ven producto</div>
            <div class="funnel-value" style="color:var(--warning)">2,890</div>
            <div class="funnel-bar" style="width:34%;background:var(--warning)"></div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">34% llega a ficha</div>
        </div>
        <div class="funnel-step">
            <div class="funnel-label">Se registran</div>
            <div class="funnel-value" style="color:var(--danger)">1,240</div>
            <div class="funnel-bar" style="width:15%;background:var(--danger)"></div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">15% inicia registro</div>
        </div>
        <div class="funnel-step">
            <div class="funnel-label">Llegan al carrito</div>
            <div class="funnel-value" style="color:var(--success)">890</div>
            <div class="funnel-bar" style="width:11%;background:var(--success)"></div>
            <div style="font-size:11px;color:var(--muted);margin-top:4px">11% agrega al carrito</div>
        </div>
    </div>

    <div class="kpi-grid">
        <div class="kpi">
            <div class="kpi-label">Bounce Rate General</div>
            <div class="kpi-value">{ga4['bounce_rate']}%</div>
            <div class="kpi-sub">Normal para B2B (rango 40-55%)</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Sesiones desde Email</div>
            <div class="kpi-value">{ga4['sesiones_email']:,}</div>
            <div class="kpi-sub">Tráfico generado por MailUp</div>
        </div>
        <div class="kpi">
            <div class="kpi-label">Tasa Apertura Email</div>
            <div class="kpi-value">{mailing['tasa_apertura']}%</div>
            <div class="kpi-sub">{mailing['enviados']:,} envíos · {mailing['clics']} clics</div>
        </div>
    </div>

    <div class="table-wrap">
        <div class="table-header">
            <h3>Bounce Rate por Sección</h3>
        </div>
        <table>
            <thead><tr><th>Página</th><th style="text-align:right">Visitas</th><th style="text-align:right">Bounce Rate</th><th>Diagnóstico</th></tr></thead>
            <tbody>{landing_rows}</tbody>
        </table>
    </div>

    <div class="insight-blue insight">
        <strong>Lectura del embudo:</strong> De cada 100 visitantes, 38 navegan catálogos, 34 ven un producto, pero solo 15 intentan registrarse y 11 llegan al carrito.
        La mayor caída es entre "ver producto" y "registrarse" — <strong>mejorar el flujo de registro podría duplicar la conversión</strong>.
    </div>
</div>

<!-- ================================ LABORATORIOS ================================ -->
<div class="section" id="laboratorios">
    <h2>Laboratorios — Rotación por Proveedor</h2>
    <div class="insight">Top laboratorios ordenados por rotación en los últimos 3 meses (unidades vendidas).</div>

    <div class="chart-box">
        <h3>Top 10 Laboratorios — Rotación 3 Meses (unidades)</h3>
        <canvas id="chartLabs" height="280"></canvas>
    </div>
</div>

<!-- ================================ SCRIPTS ================================ -->
<script>
// Tab switching
function showTab(id) {{
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
    document.querySelectorAll('.nav button').forEach(b => b.classList.remove('active'));
    document.getElementById(id).classList.add('active');
    event.target.classList.add('active');
    // Init charts when tab shown
    setTimeout(() => initCharts(), 100);
}}

// Table filter
function filterTable(tableId, query) {{
    const rows = document.querySelectorAll('#' + tableId + ' tbody tr');
    const q = query.toLowerCase();
    rows.forEach(r => {{
        r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
    }});
}}

// Column filter (vendedores)
function filterTableCol(tableId, colIdx, value) {{
    const rows = document.querySelectorAll('#' + tableId + ' tbody tr');
    rows.forEach(r => {{
        if (!value) {{ r.style.display = ''; return; }}
        const cell = r.cells[colIdx];
        r.style.display = cell && cell.textContent.trim() === value ? '' : 'none';
    }});
}}

// CSV Export
function exportTable(tableId, filename) {{
    const table = document.getElementById(tableId);
    let csv = [];
    const rows = table.querySelectorAll('tr');
    rows.forEach(r => {{
        if (r.style.display === 'none') return;
        let cols = [];
        r.querySelectorAll('th, td').forEach(c => cols.push('"' + c.textContent.replace(/"/g, '""') + '"'));
        csv.push(cols.join(','));
    }});
    const blob = new Blob([csv.join('\\n')], {{type: 'text/csv;charset=utf-8;'}});
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}}

// Charts
let chartsInit = false;
function initCharts() {{
    if (chartsInit) return;
    chartsInit = true;

    const colors = {{
        primary: '#0DA7EE', dark: '#0688E2', success: '#27ae60',
        danger: '#e74c3c', warning: '#f39c12', purple: '#9b59b6'
    }};

    // Ventas 6m
    new Chart(document.getElementById('chartVentas6m'), {{
        type: 'line',
        data: {{
            labels: {month_labels},
            datasets: [{{
                label: 'Ventas ($M)',
                data: {month_ventas},
                borderColor: colors.primary,
                backgroundColor: colors.primary + '22',
                fill: true,
                tension: 0.3,
                pointRadius: 5,
                pointBackgroundColor: colors.primary
            }}]
        }},
        options: {{ responsive:true, plugins:{{ legend:{{ display:false }} }} }}
    }});

    // Unidades 6m
    new Chart(document.getElementById('chartUnidades6m'), {{
        type: 'bar',
        data: {{
            labels: {month_labels},
            datasets: [{{
                label: 'Unidades',
                data: {month_unidades},
                backgroundColor: colors.dark + 'cc',
                borderRadius: 6
            }}]
        }},
        options: {{ responsive:true, plugins:{{ legend:{{ display:false }} }} }}
    }});

    // Campaign charts
    if (document.getElementById('chartCampVentas')) {{
        new Chart(document.getElementById('chartCampVentas'), {{
            type: 'bar',
            data: {{
                labels: {month_labels},
                datasets: [{{
                    label: 'Ventas ($M)',
                    data: {month_ventas},
                    backgroundColor: [colors.primary, colors.dark, colors.success, colors.warning, colors.danger, colors.purple],
                    borderRadius: 6
                }}]
            }},
            options: {{ responsive:true, indexAxis:'y', plugins:{{ legend:{{ display:false }} }} }}
        }});
        new Chart(document.getElementById('chartCampUnid'), {{
            type: 'line',
            data: {{
                labels: {month_labels},
                datasets: [
                    {{ label:'Unidades', data:{month_unidades}, borderColor:colors.primary, yAxisID:'y', tension:0.3, pointRadius:4 }},
                    {{ label:'Campañas', data:{month_camps}, borderColor:colors.warning, yAxisID:'y1', tension:0.3, borderDash:[5,5], pointRadius:4 }}
                ]
            }},
            options: {{ responsive:true, scales:{{ y:{{ position:'left' }}, y1:{{ position:'right', grid:{{ drawOnChartArea:false }} }} }} }}
        }});
    }}

    // Pareto
    if (document.getElementById('chartPareto')) {{
        const n = {clientes['total_clientes']};
        const pareto = {clientes['pareto_n80']};
        new Chart(document.getElementById('chartPareto'), {{
            type: 'doughnut',
            data: {{
                labels: ['Top ' + pareto + ' (80% venta)', 'Resto ' + (n - pareto) + ' clientes (20% venta)'],
                datasets: [{{ data: [pareto, n - pareto], backgroundColor: [colors.primary, '#e8ecf1'], borderWidth: 0 }}]
            }},
            options: {{ responsive:true, cutout:'65%', plugins:{{ legend:{{ position:'bottom' }} }} }}
        }});
    }}

    // Vendedores
    if (document.getElementById('chartVendedores')) {{
        const vData = {json.dumps([{'n': v['nombre'][:15], 'v': round(v['venta']/1_000_000)} for v in clientes['vendedores']])};
        new Chart(document.getElementById('chartVendedores'), {{
            type: 'bar',
            data: {{
                labels: vData.map(d => d.n),
                datasets: [{{ label:'Venta ($M)', data: vData.map(d => d.v), backgroundColor: colors.primary + 'cc', borderRadius: 6 }}]
            }},
            options: {{ responsive:true, indexAxis:'y', plugins:{{ legend:{{ display:false }} }} }}
        }});
    }}

    // SKU estados
    if (document.getElementById('chartSKU')) {{
        new Chart(document.getElementById('chartSKU'), {{
            type: 'doughnut',
            data: {{
                labels: ['Con Rotación ({skus["estados"].get("Con Rotación",0):,})', 'Abandonados ({skus["estados"].get("Abandonados",0):,})', 'Nunca Vendidos ({skus["estados"].get("Nunca Rotados",0):,})'],
                datasets: [{{ data: [{skus['estados'].get('Con Rotación',0)}, {skus['estados'].get('Abandonados',0)}, {skus['estados'].get('Nunca Rotados',0)}],
                    backgroundColor: [colors.success, colors.warning, colors.danger], borderWidth: 0 }}]
            }},
            options: {{ responsive:true, cutout:'60%', plugins:{{ legend:{{ position:'bottom' }} }} }}
        }});
    }}

    // Labs
    if (document.getElementById('chartLabs')) {{
        new Chart(document.getElementById('chartLabs'), {{
            type: 'bar',
            data: {{
                labels: {lab_names},
                datasets: [{{ label:'Rotación 3M (unid)', data:{lab_rot}, backgroundColor: colors.dark + 'cc', borderRadius: 6 }}]
            }},
            options: {{ responsive:true, indexAxis:'y', plugins:{{ legend:{{ display:false }} }} }}
        }});
    }}
}}

// Init on load
document.addEventListener('DOMContentLoaded', () => setTimeout(initCharts, 200));
</script>

</body>
</html>
"""

# Write outputs
DOCS_DIR = os.path.join(DATA_DIR, '..', 'docs')
os.makedirs(DOCS_DIR, exist_ok=True)
output = os.path.join(DOCS_DIR, 'index.html')
with open(output, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"Dashboard v6: {output}")
print(f"Size: {len(HTML)/1024:.1f} KB, {HTML.count(chr(10))} lines")
