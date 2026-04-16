# ecommerce-b2b — Dashboard ClinicalMarket

Dashboard operativo mensual de ClinicalMarket B2B. Analiza campañas Publitas, mailing MailUp, comportamiento GA4, top clientes (CDP) y performance del canal retail.

## Ver dashboard en vivo

https://roda-code.github.io/ecommerce-b2b/

## Workflow mensual (cómo actualizar los datos)

Cada inicio de mes, actualizar los archivos JSON en `data/` y hacer push a `main`. La GitHub Action regenera `docs/index.html` automáticamente.

### Archivos a actualizar

| Archivo | Fuente | Qué contiene |
|---------|--------|--------------|
| `clientes_data.json` | SAP / Power BI | Top clientes, vendedores, Pareto |
| `comparativo.json` | Power BI | Comparativo mes actual vs año anterior, campañas, top SKUs |
| `sku_data.json` | SAP | Estados del catálogo, quiebres de stock, laboratorios |
| `campanas_mensuales.json` | Power BI | Ventas y unidades por mes (últimos 6 meses) |
| `ga4_visitas.json` | GA4 | Visitas por fuente y visitas mensuales al B2B |
| `campanas_digitales.json` | GA4 + Publitas | Performance de cada campaña digital (visitas, clics, compras) |
| `productos_digital.json` | GA4 + Publitas | Top 10 productos más clickeados desde catálogos |
| `mailing.json` | MailUp | Agregar un nuevo registro por cada envío de mailing |

### Pasos

1. Exportar los datos de cada fuente y actualizar los JSONs correspondientes.
2. Push a `main`.
3. GitHub Actions ejecuta `src/build_dashboard.py` que lee todos los JSONs y genera `docs/index.html`.
4. GitHub Pages publica la nueva versión automáticamente.

## Estructura

```
ecommerce-b2b/
├── data/
│   ├── clientes_data.json          # SAP — clientes y ventas
│   ├── comparativo.json            # Power BI — comparativo mensual
│   ├── sku_data.json               # SAP — catálogo y rotación
│   ├── campanas_mensuales.json     # Power BI — ventas por mes
│   ├── ga4_visitas.json            # GA4 — tráfico y visitas
│   ├── campanas_digitales.json     # GA4+Publitas — campañas digitales
│   ├── productos_digital.json      # GA4+Publitas — top productos
│   └── mailing.json                # MailUp — historial de envíos
├── src/
│   └── build_dashboard.py          # Generador (lee JSONs → HTML)
├── docs/
│   └── index.html                  # Dashboard publicado (GitHub Pages)
├── .github/workflows/
│   └── refresh.yml                 # Auto-rebuild en cada push
└── README.md
```

## Fuentes de datos

| Sistema     | Qué entrega                                        |
|-------------|----------------------------------------------------|
| SAP         | Ventas reales por cliente (fuente de verdad)       |
| Power BI    | Reportes consolidados y comparativos               |
| Publitas    | Campañas, vistas, clicks de catálogos digitales    |
| GA4         | Tráfico web, bounce rate, comportamiento usuario   |
| MailUp      | Envíos de mailing, aperturas, CTR                   |

## Filosofía

Mes a mes vemos qué campañas funcionaron + qué mailings convirtieron + qué clientes están activos para decidir:
- A qué clientes impactar el próximo mes
- Qué campañas relanzar o pausar
- Cómo segmentar comunicaciones según el segmento CDP

---

Generado y mantenido por Rodrigo Arévalo · Ecosistema ClinicalMarket / Gesmed / Profar.
