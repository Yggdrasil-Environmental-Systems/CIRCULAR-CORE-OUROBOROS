"""
FREYJA INTERACTIVE CHARTS SUITE | CIRCULAR-CORE: OUROBOROS (0x05)
===================================================================
Institutional Dark Mode Dynamic Visualizations Powered by Plotly
Compliant with Freyja Obsidian Void UI Standard (UCPS-v1).

Lead Systems Architect: Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7)
Ecosystem: Yggdrasil Environmental Systems
"""

from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ==============================================================================
# CANONICAL FREYJA OBSIDIAN VOID PALETTE
# ==============================================================================
FREYJA_PALETTE = {
    "bg_void": "#070B12",
    "bg_card": "#0B0F17",
    "bg_plot": "#101622",
    "border": "#1E293B",
    "grid": "rgba(148, 163, 184, 0.10)",
    "text_primary": "#F8FAFC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "neon_green": "#30D158",
    "neon_cyan": "#00F0FF",
    "bio_danger": "#FF453A",
    "warning_amber": "#F6E05E",
    "royal_purple": "#A855F7",
    "soft_blue": "#38BDF8"
}


def apply_freyja_layout(
    fig: go.Figure,
    title: str = "",
    subtitle: str = "",
    height: int = 420,
    show_legend: bool = True,
    hovermode: str = "x unified"
) -> go.Figure:
    """Applies canonical Freyja Obsidian Void styling to any Plotly figure."""
    title_text = f"<b>{title}</b>"
    if subtitle:
        title_text += f"<br><span style='font-size: 0.72rem; color: {FREYJA_PALETTE['text_muted']}; font-weight: 400;'>{subtitle}</span>"

    fig.update_layout(
        paper_bgcolor=FREYJA_PALETTE["bg_card"],
        plot_bgcolor=FREYJA_PALETTE["bg_plot"],
        height=height,
        margin=dict(l=45, r=30, t=55 if subtitle else 45, b=40),
        title=dict(
            text=title_text,
            font=dict(family="Space Grotesk, Inter, sans-serif", size=14, color=FREYJA_PALETTE["text_primary"]),
            x=0.01,
            y=0.96
        ),
        font=dict(family="Inter, sans-serif", size=11, color=FREYJA_PALETTE["text_secondary"]),
        hovermode=hovermode,
        hoverlabel=dict(
            bgcolor=FREYJA_PALETTE["bg_card"],
            bordercolor=FREYJA_PALETTE["border"],
            font=dict(family="JetBrains Mono, monospace", size=11, color=FREYJA_PALETTE["text_primary"])
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(11, 15, 23, 0.7)",
            bordercolor=FREYJA_PALETTE["border"],
            borderwidth=1,
            font=dict(size=10, color=FREYJA_PALETTE["text_secondary"])
        ) if show_legend else dict(visible=False),
        xaxis=dict(
            showgrid=True,
            gridcolor=FREYJA_PALETTE["grid"],
            linecolor=FREYJA_PALETTE["border"],
            zerolinecolor=FREYJA_PALETTE["border"],
            tickfont=dict(family="JetBrains Mono, monospace", size=10, color=FREYJA_PALETTE["text_muted"])
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor=FREYJA_PALETTE["grid"],
            linecolor=FREYJA_PALETTE["border"],
            zerolinecolor=FREYJA_PALETTE["border"],
            tickfont=dict(family="JetBrains Mono, monospace", size=10, color=FREYJA_PALETTE["text_muted"])
        )
    )
    return fig


# ==============================================================================
# 1. ROOM 1: HISTORICAL CLINICAL METABOLISM CHART (25 AUDITED MONTHS)
# ==============================================================================
def create_clinical_metabolism_chart(
    df_series: pd.DataFrame,
    is_en: bool = False
) -> go.Figure:
    """
    Dynamic dual-axis area/line chart:
    - Primary Y: Waste Mass (kg) comparing Biohazard (LER 18 01 03*) and Common Waste (LER 20 03 01).
    - Secondary Y: Bag Filling Ratio / Weight per Bag (kg/bag).
    - Bottom range slider to scroll seamlessly across 25 audited months.
    """
    fig = make_subplots(
        specs=[[{"secondary_y": True}]],
        shared_xaxes=True
    )

    periods = df_series["period"].tolist()
    bio_vals = df_series["bio_kg"].tolist() if "bio_kg" in df_series.columns else df_series.iloc[:, 1].tolist()
    com_vals = df_series["common_kg"].tolist() if "common_kg" in df_series.columns else df_series.iloc[:, 2].tolist()

    # Calculate metrics
    ratios = [f"{(b / max(1e-3, c)) * 100:.1f}%" for b, c in zip(bio_vals, com_vals)]

    # Trace 1: Common Municipal Waste (LER 20 03 01)
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=com_vals,
            name="Common Waste (LER 20 03 01)" if is_en else "Residuo Común (LER 20 03 01)",
            mode="lines+markers",
            line=dict(color=FREYJA_PALETTE["neon_cyan"], width=2.5),
            marker=dict(size=5, color=FREYJA_PALETTE["neon_cyan"]),
            fill="tozeroy",
            fillcolor="rgba(0, 240, 255, 0.08)",
            hovertemplate="<b>Common:</b> %{y:.2f} kg<extra></extra>"
        ),
        secondary_y=False
    )

    # Trace 2: Biohazardous Clinical Waste (LER 18 01 03*)
    fig.add_trace(
        go.Scatter(
            x=periods,
            y=bio_vals,
            name="Biohazard Waste (LER 18 01 03*)" if is_en else "Biorriesgo (LER 18 01 03*)",
            mode="lines+markers",
            line=dict(color=FREYJA_PALETTE["bio_danger"], width=2.5),
            marker=dict(size=6, color=FREYJA_PALETTE["bio_danger"]),
            fill="tozeroy",
            fillcolor="rgba(255, 69, 58, 0.15)",
            hovertemplate="<b>Biohazard:</b> %{y:.2f} kg<extra></extra>"
        ),
        secondary_y=False
    )

    # Highlight Month 21 Spike if present
    if len(periods) > 20 and bio_vals[20] > 50:
        fig.add_annotation(
            x=periods[20],
            y=bio_vals[20],
            text="🚨 Purga M21 (94.15 kg)",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowcolor=FREYJA_PALETTE["bio_danger"],
            ax=-40,
            ay=-35,
            font=dict(color=FREYJA_PALETTE["bio_danger"], size=10, family="JetBrains Mono, monospace"),
            bgcolor="rgba(255, 69, 58, 0.2)",
            bordercolor=FREYJA_PALETTE["bio_danger"],
            borderwidth=1,
            secondary_y=False
        )

    apply_freyja_layout(
        fig,
        title="Continuous Audited Metabolism Time Series (25 Months)" if is_en else "Serie Temporal Auditada del Metabolismo Asistencial (25 Meses)",
        subtitle="Empirical mass balance across 23 clinical departments (Facility Alpha)" if is_en else "Balance gravimétrico empírico en 23 servicios clínicos (Facility Alpha)",
        height=440
    )

    fig.update_xaxes(
        rangeslider=dict(visible=True, thickness=0.08, bgcolor=FREYJA_PALETTE["bg_card"]),
        type="category"
    )
    fig.update_yaxes(title_text="Mass (kg / month)" if is_en else "Masa (kg / mes)", secondary_y=False)
    return fig


# ==============================================================================
# 2. ROOM 5: NIR OPTICAL SPECTRAL REFLECTANCE SCANNER
# ==============================================================================
def create_nir_spectra_chart(
    wavelengths: List[float],
    sample_curve: List[float],
    polymer_key: str,
    polymer_desc: str = "",
    is_complex: bool = False,
    is_en: bool = False
) -> go.Figure:
    """
    Interactive optical reflectance curve (900 - 1750 nm) for NIR polymer sorting:
    - Glowing spectral signature with peak identification.
    - Shaded bands for typical polymer absorption overtones.
    - Real-time SAM confidence marker.
    """
    fig = go.Figure()

    main_color = FREYJA_PALETTE["bio_danger"] if is_complex else FREYJA_PALETTE["neon_cyan"]
    fill_color = "rgba(255, 69, 58, 0.12)" if is_complex else "rgba(0, 240, 255, 0.12)"

    clean_poly = polymer_key.replace("_", " ")
    # Base curve
    fig.add_trace(
        go.Scatter(
            x=wavelengths,
            y=sample_curve,
            name=f"{clean_poly} Reflectance",
            mode="lines",
            line=dict(color=main_color, width=3, shape="spline"),
            fill="tozeroy",
            fillcolor=fill_color,
            hovertemplate="<b>λ:</b> %{x} nm<br><b>Reflectance:</b> %{y:.1f}%<extra></extra>"
        )
    )

    # Characteristic overtone marker zones (e.g. 1215 nm C-H second overtone, 1400 nm O-H, 1660 nm C-H first overtone)
    notable_bands = [
        (1215, "C-H 2nd Overtone", "rgba(148, 163, 184, 0.08)"),
        (1400, "O-H Combination", "rgba(148, 163, 184, 0.08)"),
        (1660, "C-H 1st Overtone", "rgba(148, 163, 184, 0.08)")
    ]

    for band_wl, band_name, band_col in notable_bands:
        fig.add_vline(
            x=band_wl,
            line_width=1,
            line_dash="dot",
            line_color=FREYJA_PALETTE["text_muted"],
            annotation_text=band_name,
            annotation_position="top left",
            annotation_font=dict(size=9, color=FREYJA_PALETTE["text_muted"])
        )

    apply_freyja_layout(
        fig,
        title=f"Optical NIR Signature: {clean_poly} ({polymer_desc})" if polymer_desc else f"Optical NIR Signature: {clean_poly}",
        subtitle="Spectral Reflectance Curve (900 - 1750 nm) · European Circular Sorting Standard" if is_en else "Curva Espectral de Reflectancia (900 - 1.750 nm) · Estándar Europeo de Triaje Óptico",
        height=380,
        show_legend=False
    )

    fig.update_xaxes(title_text="Wavelength λ (nm)" if is_en else "Longitud de Onda λ (nm)")
    fig.update_yaxes(title_text="Reflectance (%)" if is_en else "Reflectancia (%)", range=[0, 100])
    return fig


# ==============================================================================
# 3. ROOM 6: LIVE AUTOENCODER ANOMALY MSE SCORE TIMELINE
# ==============================================================================
def create_anomaly_score_chart(
    meses: List[str],
    mse_scores: List[float],
    umbral_alerta: float,
    is_en: bool = False
) -> go.Figure:
    """
    Interactive Anomaly Timeline:
    - Glowing bars color-coded by severity (Green for Normal, Red for Anomaly).
    - Horizontal dashed MAD cutoff line.
    - Highlight on Month 21 historical purge.
    """
    colors = [
        FREYJA_PALETTE["bio_danger"] if s > umbral_alerta else FREYJA_PALETTE["neon_green"]
        for s in mse_scores
    ]

    fig = go.Figure()

    # Bar trace
    fig.add_trace(
        go.Bar(
            x=meses,
            y=mse_scores,
            name="Reconstruction MSE Score" if is_en else "Score MSE Reconstrucción",
            marker=dict(
                color=colors,
                line=dict(color=FREYJA_PALETTE["border"], width=1)
            ),
            hovertemplate="<b>Period:</b> %{x}<br><b>Reconstruction MSE:</b> %{y:.4f}<extra></extra>"
        )
    )

    # Threshold line
    fig.add_shape(
        type="line",
        x0=meses[0],
        x1=meses[-1],
        y0=umbral_alerta,
        y1=umbral_alerta,
        line=dict(color=FREYJA_PALETTE["warning_amber"], width=2, dash="dash"),
        name="MAD 85% Cutoff"
    )

    fig.add_annotation(
        x=meses[int(len(meses) * 0.4)],
        y=umbral_alerta * 1.05,
        text=f"MAD 85th Percentile Threshold ({umbral_alerta:.4f})" if is_en else f"Umbral Dinámico MAD Percentil 85 ({umbral_alerta:.4f})",
        showarrow=False,
        font=dict(color=FREYJA_PALETTE["warning_amber"], size=10, family="JetBrains Mono, monospace")
    )

    # Annotate Month 21 Spike if present
    if len(meses) > 20 and mse_scores[20] > umbral_alerta:
        fig.add_annotation(
            x=meses[20],
            y=mse_scores[20],
            text="🚨 Purga M21 (94.15 kg)",
            showarrow=True,
            arrowhead=2,
            arrowcolor=FREYJA_PALETTE["bio_danger"],
            ax=0,
            ay=-30,
            font=dict(color=FREYJA_PALETTE["bio_danger"], size=10, family="JetBrains Mono, monospace"),
            bgcolor="rgba(255, 69, 58, 0.2)",
            bordercolor=FREYJA_PALETTE["bio_danger"],
            borderwidth=1
        )

    apply_freyja_layout(
        fig,
        title="OuroborosAnomalyNet: Reconstruction Drift & Outlier Tracker" if is_en else "OuroborosAnomalyNet: Monitor de Deriva de Segregación y Fraude de Pesajes",
        subtitle="Live Latent Manifold Z ∈ ℝ⁴ · Huber Reconstruction Loss" if is_en else "Espacio Latente Z ∈ ℝ⁴ · Inferencia Directa con Pérdida Huber",
        height=400,
        show_legend=False
    )

    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Reconstruction MSE Score" if is_en else "Error Cuadrático Medio (MSE)")
    return fig


# ==============================================================================
# 4. ROOM 6: ACTUARIAL DECARBONIZATION FAN CHART (2026-2030)
# ==============================================================================
def create_decarbonization_fan_chart(
    horizontes: List[str],
    p10: List[float],
    p50: List[float],
    p90: List[float],
    csrd_target: float,
    base_s3: float = 1.85,
    p05: Optional[List[float]] = None,
    p25: Optional[List[float]] = None,
    p75: Optional[List[float]] = None,
    p95: Optional[List[float]] = None,
    is_en: bool = False
) -> go.Figure:
    """
    Institutional Multi-Quantile Actuarial Fan Chart:
    - P05 - P95: Extreme Uncertainty Band (Soft Blue 15% opacity)
    - P10 - P90: Actuarial Uncertainty Band (Soft Blue 30% opacity)
    - P25 - P75: Interquartile Ribbon (Neon Emerald 40% opacity)
    - P50: Median Expected Trajectory (Cyber Cyan bold line with markers)
    - CSRD 2030 Target Line (-70% net reduction)
    """
    fig = go.Figure()

    # Outer band P05 - P95 if provided
    if p05 is not None and p95 is not None:
        fig.add_trace(
            go.Scatter(
                x=horizontes,
                y=p95,
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=horizontes,
                y=p05,
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(56, 189, 248, 0.12)",
                name="Banda Extrema P05 - P95" if not is_en else "Extreme Band P05 - P95",
                hovertemplate="<b>P05:</b> %{y:.2f} tCO2e<extra></extra>"
            )
        )

    # Actuarial band P10 - P90
    fig.add_trace(
        go.Scatter(
            x=horizontes,
            y=p90,
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        )
    )
    fig.add_trace(
        go.Scatter(
            x=horizontes,
            y=p10,
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(0, 240, 255, 0.22)",
            name="Banda Actuarial P10 - P90" if not is_en else "Actuarial Band P10 - P90",
            hovertemplate="<b>P10 (Ambitious):</b> %{y:.2f} tCO2e<extra></extra>"
        )
    )

    # Interquartile band P25 - P75 if provided
    if p25 is not None and p75 is not None:
        fig.add_trace(
            go.Scatter(
                x=horizontes,
                y=p75,
                mode="lines",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip"
            )
        )
        fig.add_trace(
            go.Scatter(
                x=horizontes,
                y=p25,
                mode="lines",
                line=dict(width=0),
                fill="tonexty",
                fillcolor="rgba(48, 209, 88, 0.32)",
                name="Intercuartil P25 - P75" if not is_en else "Interquartile P25 - P75",
                hovertemplate="<b>P25:</b> %{y:.2f} tCO2e<extra></extra>"
            )
        )

    # Median P50 Line
    fig.add_trace(
        go.Scatter(
            x=horizontes,
            y=p50,
            mode="lines+markers",
            line=dict(color=FREYJA_PALETTE["neon_cyan"], width=3),
            marker=dict(size=6, color=FREYJA_PALETTE["neon_cyan"]),
            name="Mediana P50 (Esperado CSRD)" if not is_en else "Median P50 (Expected CSRD)",
            hovertemplate="<b>P50 Expected:</b> %{y:.2f} tCO2e<extra></extra>"
        )
    )

    # CSRD Target Line
    fig.add_shape(
        type="line",
        x0=horizontes[0],
        x1=horizontes[-1],
        y0=csrd_target,
        y1=csrd_target,
        line=dict(color=FREYJA_PALETTE["bio_danger"], width=2, dash="dash"),
        name="Meta -70% CSRD"
    )

    fig.add_annotation(
        x=horizontes[int(len(horizontes) * 0.75)],
        y=csrd_target * 1.05,
        text=f"Meta Vinculante CSRD 2030 (-70%: {csrd_target:.2f} tCO2e)" if not is_en else f"CSRD 2030 Target Line (-70%: {csrd_target:.2f} tCO2e)",
        showarrow=False,
        font=dict(color=FREYJA_PALETTE["bio_danger"], size=10, family="JetBrains Mono, monospace")
    )

    apply_freyja_layout(
        fig,
        title="Physics-Informed Decarbonization Fan Chart (PINN-TCN-MHA 2026-2030)" if is_en else "Trayectoria Multicuantil de Descarbonización Scope 3 (PINN-TCN-MHA 2026-2030)",
        subtitle="Strict Quantile Monotonicity Softplus Deltas · Zero Temporal Leak Causal WaveNet" if is_en else "Monotonicidad Cuantil Estricta por Construcción · Convoluciones Causales Dilatadas WaveNet",
        height=440
    )

    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Scope 3 Emissions (tCO2e / quarter)" if is_en else "Emisiones Scope 3 (tCO2e / trimestre)")
    return fig


# ==============================================================================
# 5. ROOM 3: RESTROOM OVER-SEGREGATION PARADOX INTERACTIVE BREAKDOWN
# ==============================================================================
def create_restroom_paradox_chart(is_en: bool = False) -> go.Figure:
    """
    Executive Dual-Panel Gravimetric Forensic Chart (Obsidian Void C2 Standard):
    - Left Panel: Horizontal Forensic Bar Breakdown of Red Biohazard Bag Sources
      (92.74% Patient Restrooms paper towels vs. 7.26% Genuine Clinical Areas).
    - Right Panel: Gravimetric Bag Utilization Paradox across audited periods
      comparing Virgin HDPE Bag Tare (28.0 g constant) vs. Net Waste Inside (g/bag),
      with plastic-to-total incineration share callouts.
    """
    fig = make_subplots(
        rows=1,
        cols=2,
        column_widths=[0.50, 0.50],
        horizontal_spacing=0.13,
        subplot_titles=(
            "A. Origin of Hazardous Red Bag Mass (LER 18 01 03*)" if is_en else "A. Origen Real de la Masa en Bolsas Rojas (LER 18 01 03*)",
            "B. Virgin HDPE Bag Tare (28g) vs. Net Waste per Bag" if is_en else "B. Tara Bolsa Virgen HDPE (28g) vs. Residuo Neto Interior"
        )
    )

    # Panel 1: Horizontal Forensic Bar Breakdown of Biohazard Sources
    categories = [
        "Blood & Injections<br><span style='font-size:10px;color:#64748B'>True HP9 Biohazard</span>" if is_en else "Extracciones e Inyectables<br><span style='font-size:10px;color:#64748B'>Biorriesgo Real HP9</span>",
        "Minor Surgery & Curas<br><span style='font-size:10px;color:#64748B'>True HP9 Biohazard</span>" if is_en else "Tópico y Cirugía Menor<br><span style='font-size:10px;color:#64748B'>Biorriesgo Real HP9</span>",
        "Patient Restrooms<br><span style='font-size:10px;color:#FF453A'>Paper Towels (Misclassified)</span>" if is_en else "Aseos de Pacientes<br><span style='font-size:10px;color:#FF453A'>Toallas Papel (Sobre-segregado)</span>"
    ]
    pct_values = [2.16, 5.10, 92.74]
    bar_colors = [
        "rgba(0, 240, 255, 0.85)",
        "rgba(48, 209, 88, 0.85)",
        "rgba(255, 69, 58, 0.90)"
    ]
    border_colors = [
        FREYJA_PALETTE["neon_cyan"],
        FREYJA_PALETTE["neon_green"],
        FREYJA_PALETTE["bio_danger"]
    ]

    fig.add_trace(
        go.Bar(
            y=categories,
            x=pct_values,
            orientation="h",
            width=0.52,
            marker=dict(
                color=bar_colors,
                line=dict(color=border_colors, width=1.8)
            ),
            text=[f"  <b>{v:.2f}%</b>" for v in pct_values],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(family="JetBrains Mono, monospace", size=12, color=FREYJA_PALETTE["text_primary"]),
            hovertemplate="<b>%{y}</b><br>Share of Red Bag Mass: <b>%{x:.2f}%</b><extra></extra>",
            showlegend=False
        ),
        row=1,
        col=1
    )

    # Panel 2: Grouped Bar Chart comparing Virgin HDPE Bag Tare (28.0g) vs Net Waste per Bag
    periods = ["2024 (Baseline)" if is_en else "2024 (Base)", "2025 (Audit)" if is_en else "2025 (Auditoría)", "Q1 2026 (Paradox)" if is_en else "T1 2026 (Paradoja)"]
    hdpe_bag_g = [28.0, 28.0, 28.0]
    net_waste_g = [142.5, 68.4, 35.8]

    fig.add_trace(
        go.Bar(
            x=periods,
            y=hdpe_bag_g,
            name="Virgin HDPE Bag Tare (28.0 g)" if is_en else "Tara Bolsa Virgen HDPE (28,0 g)",
            marker=dict(
                color="rgba(246, 224, 94, 0.88)",
                line=dict(color=FREYJA_PALETTE["warning_amber"], width=1.5)
            ),
            text=[f"<b>{v:.1f} g</b>" for v in hdpe_bag_g],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(family="JetBrains Mono, monospace", size=11, color=FREYJA_PALETTE["warning_amber"]),
            hovertemplate="<b>%{x}</b><br>Virgin HDPE Plastic Tare: <b>%{y:.1f} g</b><extra></extra>"
        ),
        row=1,
        col=2
    )

    fig.add_trace(
        go.Bar(
            x=periods,
            y=net_waste_g,
            name="Net Clinical Waste Inside (g)" if is_en else "Residuo Clínico Neto Interior (g)",
            marker=dict(
                color="rgba(0, 240, 255, 0.82)",
                line=dict(color=FREYJA_PALETTE["neon_cyan"], width=1.5)
            ),
            text=[f"<b>{v:.1f} g</b>" for v in net_waste_g],
            textposition="outside",
            cliponaxis=False,
            textfont=dict(family="JetBrains Mono, monospace", size=11, color=FREYJA_PALETTE["neon_cyan"]),
            hovertemplate="<b>%{x}</b><br>Net Waste Deposited: <b>%{y:.1f} g</b><extra></extra>"
        ),
        row=1,
        col=2
    )

    # Reference line at 28.0 g on Panel 2 (1:1 Plastic-to-Waste Parity Threshold)
    fig.add_hline(
        y=28.0,
        line_dash="dot",
        line_color=FREYJA_PALETTE["bio_danger"],
        line_width=1.5,
        row=1,
        col=2
    )

    fig.add_annotation(
        x=periods[-1],
        y=35.8,
        xref="x2",
        yref="y2",
        text="⚠️ 43.9% Plastic Mass!" if is_en else "⚠️ ¡43,9% del peso quemado es plástico!",
        showarrow=True,
        arrowhead=2,
        arrowcolor=FREYJA_PALETTE["bio_danger"],
        ax=-25,
        ay=-42,
        font=dict(family="JetBrains Mono, monospace", size=10, color="#FFFFFF"),
        bgcolor="rgba(255, 69, 58, 0.85)",
        bordercolor=FREYJA_PALETTE["bio_danger"],
        borderwidth=1,
        borderpad=4
    )

    apply_freyja_layout(
        fig,
        title="Forensic Gravimetric Diagnostics: Restroom Over-Segregation & HDPE Bag Paradox" if is_en else "Diagnóstico Gravimétrico Forense: Sobre-Segregación en Aseos y Paradoja de Bolsas HDPE",
        subtitle="Empirical Audit (23 Clinical Units): Eliminating red bags in public restrooms cuts hazardous thermal volume by >85%" if is_en else "Auditoría Empírica (23 Unidades): Retirar bolsas rojas de aseos públicos reduce >85% el volumen térmico peligroso",
        height=450,
        show_legend=True,
        hovermode="closest"
    )

    # Apply Obsidian Void styling uniformly across BOTH subplot axes
    fig.update_layout(
        barmode="group",
        bargap=0.28,
        bargroupgap=0.14,
        margin=dict(l=25, r=40, t=105, b=50),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.13,
            xanchor="right",
            x=1.0,
            bgcolor="rgba(11, 15, 23, 0.85)",
            bordercolor=FREYJA_PALETTE["border"],
            borderwidth=1,
            font=dict(size=10, color=FREYJA_PALETTE["text_secondary"])
        )
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor=FREYJA_PALETTE["grid"],
        linecolor=FREYJA_PALETTE["border"],
        zerolinecolor=FREYJA_PALETTE["border"],
        tickfont=dict(family="JetBrains Mono, monospace", size=10, color=FREYJA_PALETTE["text_muted"])
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=FREYJA_PALETTE["grid"],
        linecolor=FREYJA_PALETTE["border"],
        zerolinecolor=FREYJA_PALETTE["border"],
        tickfont=dict(family="JetBrains Mono, monospace", size=11, color=FREYJA_PALETTE["text_primary"])
    )

    fig.update_xaxes(range=[0, 115], title_text="Share of Total Red Bag Mass (%)" if is_en else "Cuota sobre Masa Total en Bolsa Roja (%)", row=1, col=1)
    fig.update_yaxes(showgrid=False, title_text="", row=1, col=1)
    fig.update_xaxes(showgrid=False, title_text="Audited Operational Window" if is_en else "Ventana Operativa Auditada", row=1, col=2)
    fig.update_yaxes(range=[0, 175], title_text="Grams per Red Bag (g)" if is_en else "Gramos por Bolsa Roja (g)", row=1, col=2)

    # Style subplot headers cleanly
    for annotation in fig["layout"]["annotations"]:
        if "43" not in (annotation.text or ""):
            annotation.font = dict(family="Space Grotesk, sans-serif", size=12, color=FREYJA_PALETTE["neon_cyan"])
            annotation.y = 1.03

    return fig


# ==============================================================================
# 6. ROOM 4: SPANISH LAW 7/2022 TAX WATERFALL BREAKDOWN
# ==============================================================================
def create_tax_breakdown_chart(
    fisc_res: Dict[str, Any],
    is_en: bool = False
) -> go.Figure:
    """
    Interactive Waterfall Chart breaking down:
    - Base Landfill/Incineration Surcharge
    - Non-Reusable Plastic Levy
    - Recycling Tax Deduction
    - Net Consolidated Tax
    """
    vert_tax = fisc_res["impuesto_vertido_incineracion"]["cuota_tributaria_total_eur"]
    plas_tax = fisc_res["impuesto_plastico_no_reutilizable"]["cuota_tributaria_plastico_eur"]
    saving = fisc_res["ahorro_fiscal_total_eur"]
    net_tax = (vert_tax + plas_tax) - saving

    measure = ["relative", "relative", "relative", "total"]
    x_names = [
        "Landfill Tax" if is_en else "Canon Vertedero",
        "Plastic Levy" if is_en else "Impuesto Plástico",
        "Recycling Exemption" if is_en else "Deducción Reciclaje",
        "Net Tax Due" if is_en else "Cuota Neta Liquidada"
    ]
    y_vals = [vert_tax, plas_tax, -saving, net_tax]
    text_vals = [f"{v:+.2f} €" if i < 3 else f"{v:.2f} €" for i, v in enumerate(y_vals)]

    fig = go.Figure(
        go.Waterfall(
            name="Tax Balance",
            orientation="v",
            measure=measure,
            x=x_names,
            y=y_vals,
            text=text_vals,
            textposition="outside",
            connector=dict(line=dict(color=FREYJA_PALETTE["border"], width=1)),
            increasing=dict(marker=dict(color=FREYJA_PALETTE["bio_danger"])),
            decreasing=dict(marker=dict(color=FREYJA_PALETTE["neon_green"])),
            totals=dict(marker=dict(color=FREYJA_PALETTE["neon_cyan"]))
        )
    )

    apply_freyja_layout(
        fig,
        title="Fiscal Optimization & Statutory Tax Waterfall (Law 7/2022)" if is_en else "Liquidación Tributaria Consolidada y Deducciones Ley 7/2022",
        subtitle="Landfill Surcharge (Title VII) · Plastic Levy (Arts. 67-83) · Circular Exemptions" if is_en else "Canon de Vertedero (Título VII) · Plástico No Reutilizable · Bonificación Circular",
        height=380,
        show_legend=False
    )
    fig.update_yaxes(title_text="Amount (€)" if is_en else "Importe (€)")
    return fig
