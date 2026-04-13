# ecommerce-b2b — Dashboard ClinicalMarket

Dashboard operativo mensual de ClinicalMarket B2B. Análisis de campañas Publitas, mailing MailUp, comportamiento GA4, top clientes (CDP) y performance de vendedores.

## Ver dashboard en vivo

👉 **https://[tu-usuario].github.io/ecommerce-b2b/**

## Workflow mensual (cómo actualizar los datos)

Cada inicio de mes:

1. Exportar de **Power BI** la planilla "Venta por Cliente" → guardar como `data/Venta_por_Cliente_YYYYMM.xlsx`
2. Descargar el **INFORME PDF** del mes (campañas Publitas) → guardar en `data/INFORME_YYYYMM.pdf`
3. Anotar la última campaña de **MailUp** en `data/mailing.json` (fecha, enviados, aperturas, clics)
4. Push a `main`. La GitHub Action regenera `docs/index.html` automáticamente.
5. GitHub Pages publica la nueva versión.

## Estructura

```
ecommerce-b2b/
├── data/
│   ├── Venta_por_Cliente_YYYYMM.xlsx   # SAP — drop mensual
│   ├── INFORME_YYYYMM.pdf               # Publitas — drop mensual
│   └── mailing.json                     # MailUp — agregar cada envío
├── src/
│   └── build_dashboard.py               # Generador
├── docs/
│   └── index.html                       # Dashboard publicado (GitHub Pages)
├── .github/workflows/
│   └── refresh.yml                      # Auto-rebuild en cada push
└── README.md
```

## Fuentes de datos

| Sistema     | Qué entrega                                        |
|-------------|----------------------------------------------------|
| SAP         | Ventas reales por cliente (fuente de verdad)       |
| Power BI    | Reportes consolidados                               |
| Publitas    | Campañas, vistas, clicks de catálogos digitales    |
| GA4         | Tráfico web, bounce rate, comportamiento usuario   |
| MailUp      | Envíos de mailing, aperturas, CTR                   |

## Filosofía

Mes a mes vemos qué campañas funcionaron + qué mailings convirtieron + qué clientes están activos para decidir:
- A qué clientes impactar el próximo mes
- Qué campañas relanzar o pausar
- Cómo segmentar comunicaciones según el segmento CDP

## Roadmap

Ver tab "Roadmap" en el dashboard.

---

Generado y mantenido por Rodrigo Arévalo · Ecosistema ClinicalMarket / Gesmed / Profar.
