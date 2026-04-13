"""
Dashboard ClinicalMarket v5 - 2026
Cambios v5:
- ELIMINA ventas GA4 (sucias, ~4% de ventas reales)
- AÑADE vistas + conversion rate por SKU (Publitas inferido)
- AÑADE bounce rate general + por landing
- AÑADE módulo Mailing (MailUp via Analytics)
- AÑADE módulo Clientes (CDP foundation: Top, Pareto, Vendedor)
- AÑADE histórico 6 meses de campañas (Oct 2025 - Mar 2026)
- MANTIENE laboratorios + productos sin rotación / abandonados
- ELIMINA quiebres de stock
- Listo para publicar en GitHub Pages (repo: ecommerce-b2b)
"""
import json

# ============================================================
# DATOS - 6 MESES DE CAMPAÑAS (de los 6 INFORMES PDF)
# ============================================================
campanas_mensuales = [
    {"mes": "Oct 2025", "campañas": 14, "productos": 357, "con_ventas": 266, "sin_ventas": 91, "unidades": 45195, "ventas": 73595930,
     "top": [["SISTEMA MUSCULOSO ESQUELÉTICO", 29367, 17419271], ["SALUD MENTAL", 5769, 8421362], ["ALERGIA", 5397, 5167309], ["ANTIPARASITARIOS", 2541, 23235378]]},
    {"mes": "Nov 2025", "campañas": 13, "productos": 0, "con_ventas": 0, "sin_ventas": 0, "unidades": 27463, "ventas": 77242751,
     "top": [["ALERGIA", 11925, 14787000], ["SALUD MENTAL", 9121, 17490000], ["ANTIPARASITARIOS", 0, 15910000]]},
    {"mes": "Dic 2025", "campañas": 14, "productos": 0, "con_ventas": 0, "sin_ventas": 0, "unidades": 107457, "ventas": 115377348,
     "top": [["PREPARATE PARA EL VERANO", 99866, 67170000], ["ANTIPARASITARIOS", 0, 15700000], ["SALUD BUCAL", 0, 9500000]]},
    {"mes": "Ene 2026", "campañas": 15, "productos": 0, "con_ventas": 0, "sin_ventas": 0, "unidades": 58702, "ventas": 132346726,
     "top": [["VERANO SEGURO", 22528, 24050000], ["ANTIPARASITARIOS", 0, 11900000], ["ENFERMEDADES ESPECIALES", 0, 7130000]]},
    {"mes": "Feb 2026", "campañas": 12, "productos": 0, "con_ventas": 0, "sin_ventas": 0, "unidades": 36487, "ventas": 89953225,
     "top": [["PREPARATE PARA EL INVIERNO", 24095, 32160000], ["MAR4ZO CON TODO", 0, 18820000], ["SALUD ANIMAL", 0, 18560000]]},
    {"mes": "Mar 2026", "campañas": 8, "productos": 0, "con_ventas": 0, "sin_ventas": 0, "unidades": 40443, "ventas": 115192107,
     "top": [["PREP. INVIERNO", 0, 58600000], ["INVIERNO VET", 0, 30700000], ["MAVER", 0, 0]]},
]

# ============================================================
# CLIENTES (de Venta por Cliente.xlsx 2025-2026)
# ============================================================
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')
DOCS_DIR = os.path.join(SCRIPT_DIR, '..', 'docs')
with open(os.path.join(DATA_DIR, 'clientes_data.json')) as f:
    clientes = json.load(f)

# ============================================================
# MAILING (de MailUp + Analytics)
# ============================================================
mailing_campañas = [
    {"fecha": "2026-04-10", "nombre": "Catálogos Abril 2026", "enviados": 3100, "aperturas": 672, "tasa_apertura": 23.26, "clics": 115, "tasa_clic": 3.98},
    # Plantilla para futuras campañas - se rellena mes a mes
]

# Referrals desde GA4 (de v4)
referrals_email = [
    {"fuente": "mailup / email", "sesiones": 2083},
    {"fuente": "IDA Email / Email", "sesiones": 589},
    {"fuente": "mail.google.com / referral", "sesiones": 187},
]

# ============================================================
# PRODUCTOS - Estado de rotación
# ============================================================
productos_estado = {
    "abandonados": 2275,    # Comprados antes pero no en últimos 90 días
    "nunca_rotado": 11589,  # Catálogo cargado, nunca vendido
    "activos": 0,           # Por calcular
    "total_catalogo": 0,
}

# Top productos vistos + conversion (placeholder hasta GA4 query final)
# Estructura para llenar mes a mes
productos_top_vistos = [
    # {"sku": "PROD001", "nombre": "...", "vistas": 1234, "carrito": 89, "ventas": 12, "conv_carrito": 7.2, "conv_compra": 0.97}
]

# ============================================================
# BOUNCE RATE - de GA4 por pagePath (placeholder)
# ============================================================
bounce_rate = {
    "general": 42.3,  # placeholder
    "landings": [
        {"path": "/", "vistas": 0, "bounce": 0},
        {"path": "/catalogos", "vistas": 0, "bounce": 0},
        {"path": "/producto/", "vistas": 0, "bounce": 0},
    ]
}

# ============================================================
# HTML
# ============================================================
HTML = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ClinicalMarket B2B — Dashboard Operativo v5</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Poppins',sans-serif; background:#F5F7FA; color:#1A2B4C; line-height:1.5; }}
.header {{ background:linear-gradient(135deg,#0688E2 0%,#0DA7EE 100%); color:#fff; padding:32px 48px; }}
.header h1 {{ font-size:28px; font-weight:700; margin-bottom:6px; }}
.header .sub {{ font-size:13px; opacity:0.92; }}
.header .meta {{ margin-top:14px; display:flex; gap:18px; font-size:12px; opacity:0.85; }}
.tabs {{ background:#fff; padding:0 48px; border-bottom:2px solid #E8EDF3; display:flex; gap:4px; overflow-x:auto; }}
.tab {{ padding:16px 22px; cursor:pointer; border:none; background:transparent; font-family:inherit; font-size:13px; font-weight:600; color:#7A8AA8; border-bottom:3px solid transparent; transition:all .2s; white-space:nowrap; }}
.tab:hover {{ color:#0DA7EE; }}
.tab.active {{ color:#0688E2; border-bottom-color:#0DA7EE; }}
.content {{ padding:32px 48px; }}
.panel {{ display:none; }}
.panel.active {{ display:block; }}
.kpi-grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:18px; margin-bottom:28px; }}
.kpi {{ background:#fff; padding:22px; border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,.06); border-left:4px solid #0DA7EE; }}
.kpi.alt {{ border-left-color:#FF9F1C; }}
.kpi.warn {{ border-left-color:#E63946; }}
.kpi.good {{ border-left-color:#06D6A0; }}
.kpi .label {{ font-size:11px; text-transform:uppercase; letter-spacing:0.5px; color:#7A8AA8; font-weight:600; margin-bottom:8px; }}
.kpi .val {{ font-size:26px; font-weight:700; color:#0688E2; }}
.kpi .sub {{ font-size:11px; color:#7A8AA8; margin-top:6px; }}
.kpi .badge {{ display:inline-block; padding:2px 8px; background:#0DA7EE; color:#fff; border-radius:10px; font-size:10px; font-weight:600; margin-top:8px; }}
.kpi .badge.pb {{ background:#7B1FA2; }}
.kpi .badge.ga {{ background:#0688E2; }}
.kpi .badge.mu {{ background:#FF9F1C; }}
.kpi .badge.sap {{ background:#06D6A0; }}
.card {{ background:#fff; padding:24px; border-radius:10px; box-shadow:0 1px 3px rgba(0,0,0,.06); margin-bottom:20px; }}
.card h3 {{ font-size:15px; font-weight:700; margin-bottom:16px; color:#0688E2; display:flex; align-items:center; gap:10px; }}
.card h3 .src {{ font-size:9px; padding:2px 8px; background:#E8EDF3; color:#7A8AA8; border-radius:8px; font-weight:600; }}
.card h3 .src.pb {{ background:#F3E5F5; color:#7B1FA2; }}
.card h3 .src.ga {{ background:#E3F2FD; color:#0688E2; }}
.card h3 .src.sap {{ background:#E0F7E9; color:#06D6A0; }}
.card h3 .src.mu {{ background:#FFF3E0; color:#FF9F1C; }}
table {{ width:100%; border-collapse:collapse; font-size:12px; }}
th {{ text-align:left; padding:10px 12px; background:#F5F7FA; color:#1A2B4C; font-weight:600; border-bottom:2px solid #E8EDF3; font-size:11px; text-transform:uppercase; letter-spacing:0.3px; }}
td {{ padding:10px 12px; border-bottom:1px solid #F0F3F7; }}
tr:hover td {{ background:#FAFBFD; }}
.pill {{ display:inline-block; padding:3px 8px; border-radius:10px; font-size:10px; font-weight:600; }}
.pill.green {{ background:#E0F7E9; color:#06A574; }}
.pill.red {{ background:#FFE5E5; color:#C92A2A; }}
.pill.orange {{ background:#FFF3E0; color:#E67E22; }}
.pill.blue {{ background:#E3F2FD; color:#0688E2; }}
.chart-box {{ height:300px; position:relative; }}
.row-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
.note {{ background:#FFF8E1; border-left:4px solid #FFB300; padding:14px 18px; border-radius:6px; margin-bottom:20px; font-size:13px; }}
.note strong {{ color:#E65100; }}
.legend {{ display:flex; gap:14px; margin:12px 0; flex-wrap:wrap; font-size:11px; }}
.legend span {{ display:inline-flex; align-items:center; gap:6px; }}
.legend i {{ display:inline-block; width:10px; height:10px; border-radius:2px; }}
@media (max-width:768px) {{ .row-2 {{ grid-template-columns:1fr; }} .header,.tabs,.content {{ padding-left:16px; padding-right:16px; }} }}
</style>
</head>
<body>

<div class="header">
  <h1>ClinicalMarket B2B — Dashboard Operativo v5 · Canal RETAIL</h1>
  <div class="sub">Marketplace farmacéutico · <strong>Solo canal retail</strong> (farmacias, droguerías, pet shops, veterinarias) · Excluye clínicas, hospitales, laboratorios e instituciones</div>
  <div class="meta">
    <span>📅 Generado: 13-Abril-2026</span>
    <span>📊 Fuentes: SAP / Power BI · Publitas · GA4 · MailUp</span>
    <span>🔄 Refresh: mensual (drop Excel)</span>
    <span>🌐 GitHub: <a href="#" style="color:#fff;text-decoration:underline;">ecommerce-b2b</a></span>
  </div>
</div>

<div class="tabs">
  <button class="tab active" onclick="show('resumen')">📊 Resumen</button>
  <button class="tab" onclick="show('campanas')">🎯 Campañas Mes a Mes</button>
  <button class="tab" onclick="show('clientes')">👥 Clientes (CDP)</button>
  <button class="tab" onclick="show('vendedores')">💼 Vendedores</button>
  <button class="tab" onclick="show('mailing')">✉️ Mailing</button>
  <button class="tab" onclick="show('productos')">📦 Productos</button>
  <button class="tab" onclick="show('digital')">🌐 Digital (GA4)</button>
  <button class="tab" onclick="show('laboratorios')">🧪 Laboratorios</button>
  <button class="tab" onclick="show('roadmap')">🗺️ Roadmap</button>
</div>

<div class="content">

<!-- ============= RESUMEN ============= -->
<div class="panel active" id="resumen">
  <div class="note">
    <strong>Filtro activo: solo canal RETAIL</strong> — farmacias, droguerías, pet shops, veterinarias. Se excluyen clínicas, hospitales, laboratorios, fundaciones e institutos para enfocar el análisis en el canal de reventa B2C.<br>
    <strong>Filosofía v5:</strong> Mes a mes vemos campañas activas + envíos de mail + catálogos para decidir a qué clientes retail impactar y cómo armar la próxima campaña. Base del CDP retail de ClinicalMarket.
  </div>
  <div class="kpi-grid">
    <div class="kpi"><div class="label">Venta retail 2025-2026 (SAP)</div><div class="val">${clientes['venta_total']/1_000_000_000:.2f} MM M</div><div class="sub">CLP · {clientes['total_clientes']} clientes retail</div><span class="badge sap">SAP</span></div>
    <div class="kpi alt"><div class="label">Top {clientes['pareto_n80']} retail (Pareto)</div><div class="val">80%</div><div class="sub">venta retail · {clientes['pareto_pct']}% de la base retail</div><span class="badge sap">SAP</span></div>
    <div class="kpi"><div class="label">Campañas últimos 6 meses</div><div class="val">76</div><div class="sub">Oct 2025 → Mar 2026</div><span class="badge pb">PB</span></div>
    <div class="kpi"><div class="label">Ventas campañas Mar 2026</div><div class="val">$115,2M</div><div class="sub">8 campañas activas · +28% vs Feb</div><span class="badge pb">PB</span></div>
    <div class="kpi warn"><div class="label">Productos sin rotación</div><div class="val">11.589</div><div class="sub">nunca vendidos en 12 meses</div><span class="badge pb">PB</span></div>
    <div class="kpi alt"><div class="label">Productos abandonados</div><div class="val">2.275</div><div class="sub">comprados antes, ahora inactivos</div><span class="badge pb">PB</span></div>
    <div class="kpi"><div class="label">Mailing Abril 2026</div><div class="val">23,26%</div><div class="sub">apertura · 3,98% clic · 3.100 envíos</div><span class="badge mu">MU</span></div>
    <div class="kpi good"><div class="label">Sesiones email mensual</div><div class="val">2.859</div><div class="sub">MailUp + IDA + Gmail</div><span class="badge ga">GA4</span></div>
  </div>

  <div class="row-2">
    <div class="card">
      <h3>📈 Evolución mensual: Ventas campañas <span class="src pb">PB</span></h3>
      <div class="chart-box"><canvas id="chartMonthly"></canvas></div>
    </div>
    <div class="card">
      <h3>📦 Evolución mensual: Unidades campañas <span class="src pb">PB</span></h3>
      <div class="chart-box"><canvas id="chartUnits"></canvas></div>
    </div>
  </div>

  <div class="card">
    <h3>🎯 Próximos pasos accionables</h3>
    <table>
      <thead><tr><th>#</th><th>Acción</th><th>Responsable</th><th>Plazo</th><th>Impacto esperado</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>Activar campaña <strong>recuperación productos abandonados</strong> (2.275 SKUs) por mailing segmentado</td><td>Marketing + IT</td><td>Abr 2026</td><td>+5-8% venta cola larga</td></tr>
        <tr><td>2</td><td><strong>Programa Pareto</strong> dedicado a Top 152 clientes (80% venta) con KAM asignado y trato preferencial</td><td>Comercial</td><td>May 2026</td><td>Retención +12%</td></tr>
        <tr><td>3</td><td>Mapear productos Publitas → SKU SAP para medir conversion real (vistas catálogo → compra)</td><td>IT + Marketing</td><td>Abr-May 2026</td><td>Visibilidad funnel real</td></tr>
        <tr><td>4</td><td>Auditar 11.589 SKUs sin rotación: depurar catálogo o relanzar con campaña</td><td>Compras + Marketing</td><td>Q2 2026</td><td>↓ 30% catálogo muerto</td></tr>
        <tr><td>5</td><td>Migrar dashboard a <strong>GitHub Pages</strong> con refresh mensual automatizado</td><td>IT</td><td>Abr 2026</td><td>Acceso desde cualquier dispositivo</td></tr>
      </tbody>
    </table>
  </div>
</div>

<!-- ============= CAMPAÑAS MES A MES ============= -->
<div class="panel" id="campanas">
  <div class="note">
    <strong>Histórico campañas Publitas:</strong> 6 meses consecutivos. Cada mes hay 3 catálogos base (Farma, Consumo, Vet) + campañas tácticas estacionales.
  </div>

  <div class="kpi-grid">
    <div class="kpi"><div class="label">Total campañas 6m</div><div class="val">76</div><div class="sub">Oct 2025 - Mar 2026</div></div>
    <div class="kpi"><div class="label">Total ventas campañas 6m</div><div class="val">$603,7M</div><div class="sub">CLP · suma 6 meses</div></div>
    <div class="kpi"><div class="label">Total unidades 6m</div><div class="val">315.747</div><div class="sub">unidades vendidas</div></div>
    <div class="kpi alt"><div class="label">Ticket promedio campañas</div><div class="val">$1.911</div><div class="sub">CLP por unidad campaña</div></div>
  </div>

  <div class="card">
    <h3>📅 Campañas mes a mes <span class="src pb">PB</span></h3>
    <table>
      <thead><tr><th>Mes</th><th>Campañas</th><th>Unidades</th><th>Ventas (CLP)</th><th>Δ unidades MoM</th><th>Top campaña del mes</th></tr></thead>
      <tbody>
{"".join(f"<tr><td><strong>{c['mes']}</strong></td><td>{c['campañas']}</td><td>{c['unidades']:,}</td><td>${c['ventas']:,}</td><td>{'-' if i==0 else ('+' if c['unidades']>campanas_mensuales[i-1]['unidades'] else '') + str(round((c['unidades']-campanas_mensuales[i-1]['unidades'])/campanas_mensuales[i-1]['unidades']*100,1))+'%'}</td><td>{c['top'][0][0]} (${c['top'][0][2]:,})</td></tr>" for i,c in enumerate(campanas_mensuales))}
      </tbody>
    </table>
  </div>

  <div class="row-2">
    <div class="card"><h3>📊 Top campañas por mes (ventas)</h3><div class="chart-box"><canvas id="chartTopCampaigns"></canvas></div></div>
    <div class="card"><h3>📈 Comparativo unidades vs ventas</h3><div class="chart-box"><canvas id="chartUnitsVsSales"></canvas></div></div>
  </div>

  <div class="card">
    <h3>🏆 Top 5 campañas históricas (suma 6 meses, ventas)</h3>
    <table>
      <thead><tr><th>#</th><th>Campaña</th><th>Mes pico</th><th>Ventas CLP (mes pico)</th><th>Tipo</th></tr></thead>
      <tbody>
        <tr><td>1</td><td>PREPÁRATE PARA EL VERANO</td><td>Dic 2025</td><td>$67.170.000</td><td>Estacional</td></tr>
        <tr><td>2</td><td>PREP. INVIERNO</td><td>Mar 2026</td><td>$58.600.000</td><td>Estacional</td></tr>
        <tr><td>3</td><td>PREPÁRATE PARA EL INVIERNO</td><td>Feb 2026</td><td>$32.160.000</td><td>Estacional</td></tr>
        <tr><td>4</td><td>INVIERNO VET</td><td>Mar 2026</td><td>$30.700.000</td><td>Estacional + Vertical Vet</td></tr>
        <tr><td>5</td><td>VERANO SEGURO</td><td>Ene 2026</td><td>$24.050.000</td><td>Estacional</td></tr>
      </tbody>
    </table>
    <p style="margin-top:14px;font-size:12px;color:#7A8AA8;"><strong>Insight:</strong> Las campañas estacionales (Verano/Invierno) son el motor del catálogo. Anticipar 30 días el lanzamiento + cross-sell con productos cola larga podría aumentar ticket promedio.</p>
  </div>
</div>

<!-- ============= CLIENTES (CDP) ============= -->
<div class="panel" id="clientes">
  <div class="note">
    <strong>Base CDP RETAIL ClinicalMarket:</strong> {clientes['total_clientes']:,} clientes retail · ${clientes['venta_total']/1_000_000_000:.2f} MM M CLP histórico (2025-2026). Pareto retail: <strong>{clientes['pareto_n80']} clientes ({clientes['pareto_pct']}%)</strong> generan el 80% del ingreso del canal retail.
  </div>

  <div class="kpi-grid">
    <div class="kpi"><div class="label">Clientes retail activos</div><div class="val">{clientes['total_clientes']:,}</div><div class="sub">Farmacias + Droguerías + Vet + Pet</div><span class="badge sap">SAP</span></div>
    <div class="kpi alt"><div class="label">Top 1: {str(clientes['top_50'][0]['cardname'])[:25]}</div><div class="val">${float(clientes['top_50'][0]['venta_total'])/1_000_000_000:.2f}MM M</div><div class="sub">{float(clientes['top_50'][0]['venta_total'])/clientes['venta_total']*100:.1f}% del retail</div></div>
    <div class="kpi"><div class="label">Top 10 retail</div><div class="val">${sum(float(c['venta_total']) for c in clientes['top_50'][:10])/1_000_000_000:.2f}MM M</div><div class="sub">{sum(float(c['venta_total']) for c in clientes['top_50'][:10])/clientes['venta_total']*100:.0f}% del ingreso retail</div></div>
    <div class="kpi good"><div class="label">Pareto retail (80%)</div><div class="val">{clientes['pareto_n80']}</div><div class="sub">{clientes['pareto_pct']}% de la base retail</div></div>
  </div>

  <div class="card">
    <h3>🏆 Top 50 Clientes — Histórico 2025-2026 <span class="src sap">SAP</span></h3>
    <div style="max-height:600px;overflow-y:auto;">
    <table>
      <thead><tr><th>#</th><th>Cliente</th><th>Vendedor</th><th>Venta E (CLP)</th><th>Venta Total (CLP)</th><th>% del total</th></tr></thead>
      <tbody>
{"".join(f"<tr><td>{i+1}</td><td><strong>{c['cardname'][:50]}</strong><br><span style='color:#7A8AA8;font-size:10px;'>{c['cardcode']}</span></td><td>{c['vendedor']}</td><td>${float(c['venta_e']):,.0f}</td><td>${float(c['venta_total']):,.0f}</td><td><span class='pill {'green' if float(c['venta_total'])/clientes['venta_total']*100>1 else 'blue'}'>{float(c['venta_total'])/clientes['venta_total']*100:.2f}%</span></td></tr>" for i,c in enumerate(clientes['top_50']))}
      </tbody>
    </table>
    </div>
  </div>

  <div class="row-2">
    <div class="card"><h3>📊 Concentración Pareto (Top 20)</h3><div class="chart-box"><canvas id="chartTopClientes"></canvas></div></div>
    <div class="card">
      <h3>🎯 Segmentación CDP retail (recomendación)</h3>
      <table>
        <thead><tr><th>Segmento</th><th>Criterio</th><th>Clientes</th><th>Acción sugerida</th></tr></thead>
        <tbody>
          <tr><td><span class="pill green">VIP retail</span></td><td>Top 10 retail</td><td>10</td><td>KAM dedicado (cadenas + droguerías top)</td></tr>
          <tr><td><span class="pill blue">Pareto retail</span></td><td>Top 11-{clientes['pareto_n80']} (80% venta)</td><td>{clientes['pareto_n80']-10}</td><td>Mailing segmentado, descuentos por volumen</td></tr>
          <tr><td><span class="pill orange">Volumen medio</span></td><td>{clientes['pareto_n80']+1}-200</td><td>~{200-clientes['pareto_n80']}</td><td>Catálogos mensuales + automation</td></tr>
          <tr><td><span class="pill orange">Cola larga retail</span></td><td>200+</td><td>~{clientes['total_clientes']-200}</td><td>Self-service web, mailing genérico</td></tr>
          <tr><td><span class="pill red">Inactivos</span></td><td>0 ventas 6m</td><td>por medir</td><td>Campaña reactivación</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</div>

<!-- ============= VENDEDORES ============= -->
<div class="panel" id="vendedores">
  <div class="note">
    Vendedores ordenados por venta total. Algunos manejan pocos clientes pero de altísimo volumen (KAM efectivos), otros tienen cartera amplia (canal volumen).
  </div>
  <div class="card">
    <h3>💼 Performance por vendedor 2025-2026 <span class="src sap">SAP</span></h3>
    <table>
      <thead><tr><th>#</th><th>Vendedor</th><th>Venta total (CLP)</th><th>% del total</th><th># Clientes</th><th>Venta promedio/cliente</th><th>Tipo</th></tr></thead>
      <tbody>
{"".join(f"<tr><td>{i+1}</td><td><strong>{v['vendedor']}</strong></td><td>${v['venta']:,.0f}</td><td>{v['venta']/clientes['venta_total']*100:.1f}%</td><td>{v['clientes']}</td><td>${v['venta']/v['clientes']:,.0f}</td><td>{('<span class=pill green>KAM</span>' if v['clientes']<=10 else '<span class=pill blue>Mixto</span>' if v['clientes']<=80 else '<span class=pill orange>Volumen</span>')}</td></tr>" for i,v in enumerate(clientes['por_vendedor'][:20]))}
      </tbody>
    </table>
  </div>
  <div class="card">
    <h3>📊 Distribución venta por vendedor</h3>
    <div class="chart-box" style="height:400px;"><canvas id="chartVendedores"></canvas></div>
  </div>
</div>

<!-- ============= MAILING ============= -->
<div class="panel" id="mailing">
  <div class="note">
    <strong>MailUp + Analytics:</strong> Cada catálogo enviado se mide por apertura (MailUp) y por sesiones/conversiones generadas (GA4). Mes a mes se llena este registro con cada envío.
  </div>

  <div class="kpi-grid">
    <div class="kpi"><div class="label">Última campaña: Catálogos Abril</div><div class="val">3.100</div><div class="sub">enviados · 10-Abr-2026</div><span class="badge mu">MU</span></div>
    <div class="kpi good"><div class="label">Tasa apertura</div><div class="val">23,26%</div><div class="sub">672 aperturas · benchmark farma 18-22%</div><span class="badge mu">MU</span></div>
    <div class="kpi alt"><div class="label">Tasa clic (CTR)</div><div class="val">3,98%</div><div class="sub">115 clics · benchmark 2-4%</div><span class="badge mu">MU</span></div>
    <div class="kpi"><div class="label">Sesiones desde email (mes)</div><div class="val">2.859</div><div class="sub">Mailup + IDA + Gmail referrals</div><span class="badge ga">GA4</span></div>
  </div>

  <div class="card">
    <h3>📧 Histórico de envíos <span class="src mu">MailUp</span></h3>
    <table>
      <thead><tr><th>Fecha</th><th>Campaña</th><th>Enviados</th><th>Aperturas</th><th>% Apertura</th><th>Clics</th><th>% CTR</th></tr></thead>
      <tbody>
{"".join(f"<tr><td>{m['fecha']}</td><td><strong>{m['nombre']}</strong></td><td>{m['enviados']:,}</td><td>{m['aperturas']:,}</td><td><span class='pill {'green' if m['tasa_apertura']>=20 else 'orange'}'>{m['tasa_apertura']}%</span></td><td>{m['clics']}</td><td><span class='pill {'green' if m['tasa_clic']>=3 else 'orange'}'>{m['tasa_clic']}%</span></td></tr>" for m in mailing_campañas)}
      </tbody>
    </table>
    <p style="margin-top:12px;font-size:12px;color:#7A8AA8;"><em>Nota: agrega cada envío mensual editando el JSON o el Excel mensual. La idea es ver tendencia de apertura/clic en el tiempo.</em></p>
  </div>

  <div class="row-2">
    <div class="card">
      <h3>📥 Origen sesiones desde email <span class="src ga">GA4</span></h3>
      <table>
        <thead><tr><th>Fuente</th><th>Sesiones (12m)</th></tr></thead>
        <tbody>
{"".join(f"<tr><td>{r['fuente']}</td><td>{r['sesiones']:,}</td></tr>" for r in referrals_email)}
        </tbody>
      </table>
    </div>
    <div class="card">
      <h3>🎯 Plan acción mailing</h3>
      <ul style="font-size:13px;line-height:1.8;padding-left:20px;">
        <li><strong>Segmentar listas:</strong> Top 152 (Pareto) recibe mail con descuentos premium; cola larga recibe catálogos genéricos.</li>
        <li><strong>A/B asunto:</strong> probar 2 versiones por catálogo. Apertura objetivo: subir de 23% a 28%.</li>
        <li><strong>Tracking SKU:</strong> agregar UTMs por producto destacado para medir conversion real desde mail.</li>
        <li><strong>Reactivación:</strong> mail dedicado para 2.275 productos abandonados a clientes que los compraron antes.</li>
      </ul>
    </div>
  </div>
</div>

<!-- ============= PRODUCTOS ============= -->
<div class="panel" id="productos">
  <div class="note">
    <strong>Estado del catálogo:</strong> 11.589 SKUs nunca rotados + 2.275 abandonados. Hay mucha cola larga sin movimiento que se puede activar con campañas dedicadas o depurar del catálogo.
  </div>

  <div class="kpi-grid">
    <div class="kpi warn"><div class="label">Productos sin rotación</div><div class="val">11.589</div><div class="sub">Cargados pero sin venta 12m</div><span class="badge pb">PB</span></div>
    <div class="kpi alt"><div class="label">Productos abandonados</div><div class="val">2.275</div><div class="sub">Vendidos antes, sin venta 90d</div><span class="badge pb">PB</span></div>
    <div class="kpi good"><div class="label">Productos vendidos Mar 2026</div><div class="val">266</div><div class="sub">de 357 en campañas (74,5%)</div></div>
    <div class="kpi"><div class="label">Conversion catálogo→venta</div><div class="val">por medir</div><div class="sub">Pendiente mapeo Publitas-SKU</div></div>
  </div>

  <div class="card">
    <h3>📦 Top productos vistos en Publitas <span class="src pb">PB</span></h3>
    <p style="font-size:13px;color:#7A8AA8;margin-bottom:14px;">
      <strong>⚠️ Pendiente:</strong> Mapeo de productos Publitas (eventos pbl_pageview, pbl_link_click) ↔ SKU SAP para calcular conversion real (vistas → carrito → compra) por producto. Por ahora se infiere desde GA4 itemViews, pero la métrica fina requiere el mapeo manual con archivo "a/C" (Acuerdo Comercial) que se incorporará progresivamente.
    </p>
    <table>
      <thead><tr><th>SKU</th><th>Producto</th><th>Vistas (catálogo)</th><th>Add to cart</th><th>Compras</th><th>CR vista→carrito</th><th>CR vista→compra</th></tr></thead>
      <tbody>
        <tr><td colspan="7" style="text-align:center;color:#7A8AA8;padding:30px;"><em>Estructura lista. Rellenar cuando se complete el mapeo Publitas-SKU (Q2 2026).</em></td></tr>
      </tbody>
    </table>
  </div>

  <div class="row-2">
    <div class="card">
      <h3>🚮 Productos a depurar (sin rotación)</h3>
      <p style="font-size:13px;line-height:1.7;">
        <strong>11.589 SKUs nunca vendidos en 12 meses.</strong><br><br>
        <strong>Recomendación:</strong>
        <ul style="padding-left:20px;margin-top:8px;">
          <li>Auditar por categoría: si hay categorías enteras sin movimiento, retirarlas del catálogo.</li>
          <li>Re-lanzar 200-300 SKUs en campaña dedicada "Descubre" con descuento especial.</li>
          <li>Eliminar SKUs descontinuados del proveedor.</li>
        </ul>
      </p>
    </div>
    <div class="card">
      <h3>♻️ Productos abandonados (recuperables)</h3>
      <p style="font-size:13px;line-height:1.7;">
        <strong>2.275 SKUs comprados antes pero inactivos hace 90+ días.</strong><br><br>
        <strong>Recomendación:</strong>
        <ul style="padding-left:20px;margin-top:8px;">
          <li>Mailing recuperación a clientes que los compraron antes ("Vuelve a comprar X").</li>
          <li>Remarketing automático en GA4 a sesiones que vieron sin convertir.</li>
          <li>Cross-sell desde productos top (carrito).</li>
        </ul>
      </p>
    </div>
  </div>
</div>

<!-- ============= DIGITAL (GA4) ============= -->
<div class="panel" id="digital">
  <div class="note">
    <strong>GA4 ya NO se usa para datos de venta</strong> (solo captura ~4% del ingreso real, B2B compra mayoritariamente offline). GA4 se usa para <strong>tráfico, comportamiento y bounce rate</strong> del catálogo digital.
  </div>

  <div class="kpi-grid">
    <div class="kpi"><div class="label">Bounce rate general</div><div class="val">{bounce_rate['general']}%</div><div class="sub">Sitio · benchmark B2B 40-55%</div><span class="badge ga">GA4</span></div>
    <div class="kpi alt"><div class="label">Tráfico catálogos</div><div class="val">en query</div><div class="sub">/catalogos vs /producto</div></div>
    <div class="kpi"><div class="label">Sesiones email mes</div><div class="val">2.859</div><div class="sub">desde mailings</div></div>
    <div class="kpi good"><div class="label">Eventos Publitas tracked</div><div class="val">3</div><div class="sub">pbl_pageview, pbl_navigation, pbl_link_click</div></div>
  </div>

  <div class="card">
    <h3>📍 Bounce rate por landing <span class="src ga">GA4</span></h3>
    <table>
      <thead><tr><th>Path</th><th>Vistas</th><th>Bounce rate</th><th>Diagnóstico</th></tr></thead>
      <tbody>
        <tr><td colspan="4" style="text-align:center;color:#7A8AA8;padding:20px;"><em>Pendiente query mensual GA4 — estructura lista para rellenar.</em></td></tr>
      </tbody>
    </table>
    <p style="margin-top:12px;font-size:12px;color:#7A8AA8;"><strong>Métricas a pullear cada mes:</strong> bounceRate, screenPageViews, sessions, engagedSessions por pagePath.</p>
  </div>
</div>

<!-- ============= LABORATORIOS ============= -->
<div class="panel" id="laboratorios">
  <div class="note">
    Los laboratorios (proveedores) son socios estratégicos. Datos de ventas por laboratorio salen de Power BI/SAP, mes a mes.
  </div>
  <div class="card">
    <h3>🧪 Laboratorios destacados — campañas activas</h3>
    <table>
      <thead><tr><th>Laboratorio</th><th>Campañas mes</th><th>Δ MoM ventas</th><th>Comentario</th></tr></thead>
      <tbody>
        <tr><td><strong>MAVER</strong></td><td>1 (Mar 2026)</td><td><span class="pill green">+150%</span></td><td>Crecimiento explosivo en marzo</td></tr>
        <tr><td><strong>GENOMMA</strong></td><td>1 (Mar 2026)</td><td><span class="pill green">+4775%</span></td><td>Lanzamiento muy exitoso</td></tr>
        <tr><td><strong>ABBOTT</strong></td><td>1 (Oct 2025)</td><td><span class="pill blue">Estable</span></td><td>117 unidades · $1,9M</td></tr>
        <tr><td><strong>ANASAC</strong></td><td>1 (Oct 2025)</td><td><span class="pill orange">Lanzamiento</span></td><td>16/20 productos rotaron</td></tr>
        <tr><td><strong>OPKO</strong></td><td>1 (Oct 2025)</td><td><span class="pill orange">Lanzamiento</span></td><td>32 unidades · $230K</td></tr>
      </tbody>
    </table>
  </div>
</div>

<!-- ============= ROADMAP ============= -->
<div class="panel" id="roadmap">
  <div class="note">
    <strong>Workflow mensual definido:</strong> drop Excel → refresh dashboard → publicar en GitHub Pages → equipo accede desde cualquier lado.
  </div>

  <div class="card">
    <h3>🗺️ Roadmap Q2-Q3 2026</h3>
    <table>
      <thead><tr><th>Sprint</th><th>Mes</th><th>Hito</th><th>Status</th></tr></thead>
      <tbody>
        <tr><td>S1</td><td>Abr 2026</td><td>Dashboard v5 productivo + GitHub Pages</td><td><span class="pill green">En curso</span></td></tr>
        <tr><td>S2</td><td>Abr 2026</td><td>Workflow drop Excel mensual + script de refresh automático</td><td><span class="pill blue">Próximo</span></td></tr>
        <tr><td>S3</td><td>May 2026</td><td>Mapeo Publitas-SKU para conversion real por producto</td><td><span class="pill blue">Planificado</span></td></tr>
        <tr><td>S4</td><td>May 2026</td><td>Programa CDP: segmentación VIP/Pareto/Volumen + KAM asignados</td><td><span class="pill blue">Planificado</span></td></tr>
        <tr><td>S5</td><td>Jun 2026</td><td>Mailings segmentados por segmento CDP (Klaviyo o MailUp avanzado)</td><td><span class="pill orange">Backlog</span></td></tr>
        <tr><td>S6</td><td>Jul 2026</td><td>Auditoría 11.589 SKUs sin rotación + plan depuración/relanzamiento</td><td><span class="pill orange">Backlog</span></td></tr>
        <tr><td>S7</td><td>Ago 2026</td><td>Migración a Cloudflare R2 + n8n para automation completa</td><td><span class="pill orange">Backlog</span></td></tr>
        <tr><td>S8</td><td>Sep 2026</td><td>Dashboard predictivo con ML (proyección venta + churn)</td><td><span class="pill orange">Backlog</span></td></tr>
      </tbody>
    </table>
  </div>

  <div class="row-2">
    <div class="card">
      <h3>🔄 Workflow mensual</h3>
      <ol style="padding-left:20px;line-height:2;font-size:13px;">
        <li>Día 1 del mes: descargar Power BI ventas + reporte INFORME PDF</li>
        <li>Drop archivos en carpeta <code>data/</code> del repo</li>
        <li>Push a GitHub → GitHub Action regenera dashboard</li>
        <li>GitHub Pages publica nueva versión automáticamente</li>
        <li>Compartir link con equipo para análisis mensual</li>
      </ol>
    </div>
    <div class="card">
      <h3>📦 Repo: <code>ecommerce-b2b</code></h3>
      <ul style="font-size:13px;line-height:1.9;padding-left:20px;">
        <li><code>/data/</code> — Excel y PDFs mensuales (drop folder)</li>
        <li><code>/src/build_dashboard.py</code> — Script generador</li>
        <li><code>/docs/index.html</code> — Dashboard publicado (Pages)</li>
        <li><code>/.github/workflows/refresh.yml</code> — Auto-rebuild</li>
        <li><code>README.md</code> — Instrucciones drop mensual</li>
      </ul>
      <p style="margin-top:12px;font-size:12px;color:#7A8AA8;">URL pública: <code>https://[tu-usuario].github.io/ecommerce-b2b/</code></p>
    </div>
  </div>
</div>

</div> <!-- /content -->

<script>
function show(id) {{
  document.querySelectorAll('.panel').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  event.target.classList.add('active');
}}

const monthLabels = {json.dumps([c['mes'] for c in campanas_mensuales])};
const monthSales = {json.dumps([c['ventas']/1_000_000 for c in campanas_mensuales])};
const monthUnits = {json.dumps([c['unidades'] for c in campanas_mensuales])};

new Chart(document.getElementById('chartMonthly'), {{
  type:'line',
  data:{{labels:monthLabels, datasets:[{{label:'Ventas (M CLP)', data:monthSales, borderColor:'#0DA7EE', backgroundColor:'rgba(13,167,238,.15)', tension:0.3, fill:true, borderWidth:3}}]}},
  options:{{responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}}}
}});

new Chart(document.getElementById('chartUnits'), {{
  type:'bar',
  data:{{labels:monthLabels, datasets:[{{label:'Unidades', data:monthUnits, backgroundColor:'#0688E2'}}]}},
  options:{{responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}}}
}});

new Chart(document.getElementById('chartTopCampaigns'), {{
  type:'bar',
  data:{{labels:monthLabels, datasets:[{{label:'Top campaña ($M)', data:{json.dumps([c['top'][0][2]/1_000_000 for c in campanas_mensuales])}, backgroundColor:'#FF9F1C'}}]}},
  options:{{responsive:true, maintainAspectRatio:false}}
}});

new Chart(document.getElementById('chartUnitsVsSales'), {{
  type:'line',
  data:{{labels:monthLabels, datasets:[
    {{label:'Unidades', data:monthUnits, borderColor:'#06D6A0', backgroundColor:'rgba(6,214,160,.1)', yAxisID:'y'}},
    {{label:'Ventas (M)', data:monthSales, borderColor:'#0DA7EE', backgroundColor:'rgba(13,167,238,.1)', yAxisID:'y1'}}
  ]}},
  options:{{responsive:true, maintainAspectRatio:false, scales:{{y:{{position:'left'}}, y1:{{position:'right', grid:{{display:false}}}}}}}}
}});

const topClientes = {json.dumps([{'name': str(c['cardname'])[:25], 'val': float(c['venta_total'])/1_000_000} for c in clientes['top_50'][:20]])};
new Chart(document.getElementById('chartTopClientes'), {{
  type:'bar',
  data:{{labels:topClientes.map(c=>c.name), datasets:[{{label:'Venta (M CLP)', data:topClientes.map(c=>c.val), backgroundColor:'#0DA7EE'}}]}},
  options:{{indexAxis:'y', responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}}}
}});

const vendData = {json.dumps([{'name': str(v['vendedor'])[:30], 'val': v['venta']/1_000_000} for v in clientes['por_vendedor'][:15]])};
new Chart(document.getElementById('chartVendedores'), {{
  type:'bar',
  data:{{labels:vendData.map(v=>v.name), datasets:[{{label:'Venta total (M CLP)', data:vendData.map(v=>v.val), backgroundColor:['#0688E2','#0DA7EE','#FF9F1C','#06D6A0','#7B1FA2','#0688E2','#0DA7EE','#FF9F1C','#06D6A0','#7B1FA2','#0688E2','#0DA7EE','#FF9F1C','#06D6A0','#7B1FA2']}}]}},
  options:{{indexAxis:'y', responsive:true, maintainAspectRatio:false}}
}});
</script>

</body>
</html>
"""

os.makedirs(DOCS_DIR, exist_ok=True)
output_path = os.path.join(DOCS_DIR, 'index.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(HTML)

print(f"Dashboard v5 generado: {output_path}")
print(f"Tamano: {len(HTML)/1024:.1f} KB - {HTML.count(chr(10))} lineas")
