"""CIRCULAR-CORE: OUROBOROS Components Package."""
from .kpis import render_metric_card, render_alert_banner
from .freyja_ui import (
    render_ecosystem_topbar,
    render_c2_header,
    render_kpi_card,
    render_legal_shield,
    render_sidebar_legal_badge,
)
from .interactive_charts import (
    FREYJA_PALETTE,
    apply_freyja_layout,
    create_clinical_metabolism_chart,
    create_nir_spectra_chart,
    create_anomaly_score_chart,
    create_decarbonization_fan_chart,
    create_restroom_paradox_chart,
    create_tax_breakdown_chart
)

__all__ = [
    "render_metric_card",
    "render_alert_banner",
    "render_ecosystem_topbar",
    "render_c2_header",
    "render_kpi_card",
    "render_legal_shield",
    "render_sidebar_legal_badge",
    "FREYJA_PALETTE",
    "apply_freyja_layout",
    "create_clinical_metabolism_chart",
    "create_nir_spectra_chart",
    "create_anomaly_score_chart",
    "create_decarbonization_fan_chart",
    "create_restroom_paradox_chart",
    "create_tax_breakdown_chart"
]
