"""
COMPONENTES VISUALES TUFTE / FREYJA PARA STREAMLIT
Tarjetas de métricas, sellos normativos y banners de alerta sin ruido visual (Data-to-Ink ratio >= 0.88).
"""

import streamlit as st


def render_metric_card(title: str, value: str, subtitle: str = "", delta: str = "", delta_type: str = "green"):
    badge_class = "badge-green" if delta_type == "green" else ("badge-red" if delta_type == "red" else "badge-amber")
    delta_html = f'<span class="metric-badge {badge_class}">{delta}</span>' if delta else ""
    sub_html = f'<div style="font-size:0.8rem; color:#8F9CAE; margin-top:0.2rem;">{subtitle}</div>' if subtitle else ""

    html = f"""
    <div class="metric-box">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
        {sub_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_alert_banner(title: str, message: str, level: str = "warning"):
    colors = {
        "warning": {"border": "#FF9F0A", "bg": "rgba(255, 159, 10, 0.12)", "text": "#FFB340"},
        "danger": {"border": "#FF453A", "bg": "rgba(255, 69, 58, 0.12)", "text": "#FF6961"},
        "success": {"border": "#30D158", "bg": "rgba(48, 209, 88, 0.12)", "text": "#30D158"},
        "info": {"border": "#00D2FF", "bg": "rgba(0, 210, 255, 0.12)", "text": "#00D2FF"}
    }
    c = colors.get(level, colors["warning"])
    html = f"""
    <div style="border-left: 4px solid {c['border']}; background: {c['bg']}; padding: 0.85rem 1.1rem; border-radius: 6px; margin: 0.8rem 0;">
        <strong style="color: {c['text']}; font-family: 'Space Grotesk', sans-serif;">{title}</strong>
        <p style="margin: 0.25rem 0 0 0; color: #D0D7DE; font-size: 0.88rem;">{message}</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
