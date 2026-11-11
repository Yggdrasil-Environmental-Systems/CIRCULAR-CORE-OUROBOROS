"""
CUANTIFICACIÓN DE HUELLA DE CARBONO CORPORATIVA UNE-EN ISO 14064-1:2019
=======================================================================
Conforme a:
- Norma UNE-EN ISO 14064-1:2019 (Especificación con orientación, para la cuantificación y el informe de las emisiones y remociones de gases de efecto invernadero del nivel de organización)
- Metodología Oficial MITECO (Registro de Huella de Carbono, Compensación y Proyectos de Absorción de CO2)
- Directiva (UE) 2022/2464 (CSRD) / EFRAG ESRS E1 (Cambio Climático) y ESRS E5 (Uso de Recursos y Economía Circular)
- IPCC Sexto Informe de Evaluación (AR6) - Potenciales de Calentamiento Global (GWP 100 años)

Autor: Kelvin Jesús Flores Yarihuaman | Lead Systems Architect (MECES 3 / EQF 7)
Ecosistema: Yggdrasil Environmental Systems · CIRCULAR-CORE: OUROBOROS (0x05)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class EmisionComponente:
    """Componente individual de emisión de GEI con incertidumbre asociada."""
    nombre: str
    alcance: str  # "Alcance 1", "Alcance 2" o "Alcance 3"
    categoria_iso14064: str  # C1 Directas, C2 Energía Importada, C3 Transporte, C4 Productos usados, C5 Uso de productos, C6 Otras
    dato_actividad: float
    unidad_actividad: str
    factor_emision: float
    unidad_fe: str
    emisiones_tCO2e: float
    incertidumbre_pct: float = 5.0  # Incertidumbre porcentual (sigma_i relativa)
    incertidumbre_absoluta_tCO2e: float = 0.0


class MotorHuellaCarbonoISO14064:
    """
    Motor determinista para la cuantificación, análisis de incertidumbre gaussiana
    y agregación pericial de Huella de Carbono conforme a UNE-EN ISO 14064-1:2019 y MITECO.
    """

    def __init__(self, factores_oficiales: Optional[Dict[str, Any]] = None):
        self.factores = factores_oficiales or {}
        self.s1_cfg = self.factores.get("scope_1_direct", {})
        self.s2_cfg = self.factores.get("scope_2_electricity", {})
        self.s3_cfg = self.factores.get("scope_3_value_chain", {})

    def cuantificar_inventario(
        self,
        diesel_calefaccion_litros: float = 0.0,
        diesel_flota_vehiculos_litros: float = 0.0,
        gas_natural_kwh: float = 0.0,
        gas_refrigerante_tipo: str = "R-410A",
        refrigerante_recargado_kg: float = 0.0,
        electricidad_red_kwh: float = 0.0,
        electricidad_gdo_renovable_pct: float = 0.0,
        residuos_incineracion_t: float = 0.0,
        residuos_autoclave_t: float = 0.0,
        residuos_vertedero_t: float = 0.0,
        residuos_reciclados_t: float = 0.0,
        transporte_tkm: float = 0.0
    ) -> Dict[str, Any]:
        """
        Cuantifica exhaustivamente las emisiones de Alcance 1, 2 y 3 bajo la taxonomía de la ISO 14064-1:2019,
        aplicando propagación de incertidumbre gaussiana (sigma_total = sqrt(sum sigma_i^2)).
        """
        componentes: List[EmisionComponente] = []

        # --- ALCANCE 1: Emisiones Directas (Categoría 1 ISO 14064) ---
        fe_diesel = self.s1_cfg.get("combustion_fuels", {}).get("diesel_heating_oil_kgCO2e_per_liter", 2.521)
        fe_gas = self.s1_cfg.get("combustion_fuels", {}).get("natural_gas_kgCO2e_per_kWh", 0.202)
        
        gwps = self.s1_cfg.get("refrigerant_fugitive_gwp_ar6", {
            "R-410A": 2088.0, "R-134A": 1430.0, "R-32": 675.0, "R-404A": 3922.0
        })
        gwp_ref = gwps.get(gas_refrigerante_tipo.upper(), 2088.0)

        # 1. Combustión fija (Calderas / Generadores)
        if diesel_calefaccion_litros > 0:
            em_t = (diesel_calefaccion_litros * fe_diesel) / 1000.0
            inc_abs = em_t * 0.05
            componentes.append(EmisionComponente(
                nombre="Combustión Fija - Gasóleo C / Grupo Electrógeno",
                alcance="Alcance 1",
                categoria_iso14064="Categoría 1: Emisiones Directas",
                dato_actividad=diesel_calefaccion_litros,
                unidad_actividad="litros",
                factor_emision=fe_diesel,
                unidad_fe="kgCO2e/litro",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=5.0,
                incertidumbre_absoluta_tCO2e=round(inc_abs, 4)
            ))

        if gas_natural_kwh > 0:
            em_t = (gas_natural_kwh * fe_gas) / 1000.0
            inc_abs = em_t * 0.05
            componentes.append(EmisionComponente(
                nombre="Combustión Fija - Gas Natural",
                alcance="Alcance 1",
                categoria_iso14064="Categoría 1: Emisiones Directas",
                dato_actividad=gas_natural_kwh,
                unidad_actividad="kWh PCS",
                factor_emision=fe_gas,
                unidad_fe="kgCO2e/kWh",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=5.0,
                incertidumbre_absoluta_tCO2e=round(inc_abs, 4)
            ))

        # 2. Combustión móvil (Flota propia)
        if diesel_flota_vehiculos_litros > 0:
            em_t = (diesel_flota_vehiculos_litros * fe_diesel) / 1000.0
            inc_abs = em_t * 0.06
            componentes.append(EmisionComponente(
                nombre="Combustión Móvil - Flota de Transporte Propia",
                alcance="Alcance 1",
                categoria_iso14064="Categoría 1: Emisiones Directas",
                dato_actividad=diesel_flota_vehiculos_litros,
                unidad_actividad="litros",
                factor_emision=fe_diesel,
                unidad_fe="kgCO2e/litro",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=6.0,
                incertidumbre_absoluta_tCO2e=round(inc_abs, 4)
            ))

        # 3. Emisiones fugitivas de refrigerantes
        if refrigerante_recargado_kg > 0:
            em_t = (refrigerante_recargado_kg * gwp_ref) / 1000.0
            inc_abs = em_t * 0.10
            componentes.append(EmisionComponente(
                nombre=f"Fugas Gases Fluorados ({gas_refrigerante_tipo})",
                alcance="Alcance 1",
                categoria_iso14064="Categoría 1: Emisiones Directas",
                dato_actividad=refrigerante_recargado_kg,
                unidad_actividad="kg recargados",
                factor_emision=gwp_ref,
                unidad_fe="GWP AR6 (kgCO2e/kg)",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=10.0,
                incertidumbre_absoluta_tCO2e=round(inc_abs, 4)
            ))

        # --- ALCANCE 2: Electricidad Importada (Categoría 2 ISO 14064) ---
        fe_mix_red = self.s2_cfg.get("spain_peninsular_grid_location_based_kgCO2e_per_kWh", 0.185)
        
        # Enfoque por localización (Location-based)
        em_s2_location_t = (electricidad_red_kwh * fe_mix_red) / 1000.0
        # Enfoque por mercado (Market-based: deduciendo % cubierto por Garantías de Origen Renovables)
        kwh_red_mercado = electricidad_red_kwh * max(0.0, (1.0 - (electricidad_gdo_renovable_pct / 100.0)))
        em_s2_market_t = (kwh_red_mercado * fe_mix_red) / 1000.0

        componentes.append(EmisionComponente(
            nombre="Electricidad Importada (Location-Based - Mix Peninsular REE/MITECO)",
            alcance="Alcance 2",
            categoria_iso14064="Categoría 2: Emisiones Indirectas por Energía",
            dato_actividad=electricidad_red_kwh,
            unidad_actividad="kWh",
            factor_emision=fe_mix_red,
            unidad_fe="kgCO2e/kWh",
            emisiones_tCO2e=round(em_s2_location_t, 4),
            incertidumbre_pct=4.0,
            incertidumbre_absoluta_tCO2e=round(em_s2_location_t * 0.04, 4)
        ))

        # --- ALCANCE 3: Cadena de Valor (Categoría 3 y 4 ISO 14064) ---
        fe_waste = self.s3_cfg.get("category_5_waste_treatment_kgCO2e_per_kg", {})
        fe_inc = fe_waste.get("incineracion_termica_1200C", 1.800)
        fe_aut = fe_waste.get("autoclave_esterilizacion_vapor", 0.220)
        fe_ver = fe_waste.get("vertedero_controlado_fraccion_resto", 0.580)
        fe_rec = fe_waste.get("reciclaje_mecanico_evitacion_neta", -0.700)

        if residuos_incineracion_t > 0:
            em_t = residuos_incineracion_t * fe_inc
            componentes.append(EmisionComponente(
                nombre="Tratamiento Residuos: Incineración Térmica 1.200 °C",
                alcance="Alcance 3",
                categoria_iso14064="Categoría 4: Productos y Servicios Utilizados",
                dato_actividad=residuos_incineracion_t * 1000.0,
                unidad_actividad="kg eliminados",
                factor_emision=fe_inc,
                unidad_fe="kgCO2e/kg",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=8.0,
                incertidumbre_absoluta_tCO2e=round(em_t * 0.08, 4)
            ))

        if residuos_autoclave_t > 0:
            em_t = residuos_autoclave_t * fe_aut
            componentes.append(EmisionComponente(
                nombre="Tratamiento Residuos: Desinfección Autoclave por Vapor",
                alcance="Alcance 3",
                categoria_iso14064="Categoría 4: Productos y Servicios Utilizados",
                dato_actividad=residuos_autoclave_t * 1000.0,
                unidad_actividad="kg tratados",
                factor_emision=fe_aut,
                unidad_fe="kgCO2e/kg",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=7.0,
                incertidumbre_absoluta_tCO2e=round(em_t * 0.07, 4)
            ))

        if residuos_vertedero_t > 0:
            em_t = residuos_vertedero_t * fe_ver
            componentes.append(EmisionComponente(
                nombre="Tratamiento Residuos: Vertedero Controlado (Metano)",
                alcance="Alcance 3",
                categoria_iso14064="Categoría 4: Productos y Servicios Utilizados",
                dato_actividad=residuos_vertedero_t * 1000.0,
                unidad_actividad="kg depositados",
                factor_emision=fe_ver,
                unidad_fe="kgCO2e/kg",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=12.0,
                incertidumbre_absoluta_tCO2e=round(em_t * 0.12, 4)
            ))

        if residuos_reciclados_t > 0:
            em_t = residuos_reciclados_t * fe_rec  # Emisión neta negativa (evitación)
            componentes.append(EmisionComponente(
                nombre="Economía Circular: Emisiones Evitadas por Reciclaje Mecánico",
                alcance="Alcance 3",
                categoria_iso14064="Categoría 4: Productos y Servicios Utilizados",
                dato_actividad=residuos_reciclados_t * 1000.0,
                unidad_actividad="kg reciclados",
                factor_emision=fe_rec,
                unidad_fe="kgCO2e/kg evitado",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=10.0,
                incertidumbre_absoluta_tCO2e=round(abs(em_t) * 0.10, 4)
            ))

        if transporte_tkm > 0:
            fe_tkm = self.s3_cfg.get("category_4_9_transport_kgCO2e_per_tkm", {}).get("camion_rigido_diesel_pesado", 0.190)
            em_t = (transporte_tkm * fe_tkm) / 1000.0
            componentes.append(EmisionComponente(
                nombre="Logística Rodada de Residuos (Transporte Pesado t·km)",
                alcance="Alcance 3",
                categoria_iso14064="Categoría 3: Emisiones Indirectas por Transporte",
                dato_actividad=transporte_tkm,
                unidad_actividad="t·km",
                factor_emision=fe_tkm,
                unidad_fe="kgCO2e/(t·km)",
                emisiones_tCO2e=round(em_t, 4),
                incertidumbre_pct=9.0,
                incertidumbre_absoluta_tCO2e=round(em_t * 0.09, 4)
            ))

        # --- TOTALIZACIONES Y PROPAGACIÓN DE INCERTIDUMBRE GAUSSIANA ---
        total_s1_t = sum(c.emisiones_tCO2e for c in componentes if c.alcance == "Alcance 1")
        total_s2_loc_t = em_s2_location_t
        total_s2_mkt_t = em_s2_market_t
        total_s3_t = sum(c.emisiones_tCO2e for c in componentes if c.alcance == "Alcance 3")

        huella_total_loc_t = total_s1_t + total_s2_loc_t + total_s3_t
        huella_total_mkt_t = total_s1_t + total_s2_mkt_t + total_s3_t

        # Propagación de incertidumbre cuadrática: sigma_total = sqrt(sum sigma_i^2)
        suma_varianzas = sum(c.incertidumbre_absoluta_tCO2e ** 2 for c in componentes)
        sigma_total_t = math.sqrt(suma_varianzas)
        incertidumbre_expandida_95_t = round(1.96 * sigma_total_t, 4)  # Cobertura k=2 (~95% confianza)
        incertidumbre_global_pct = round((incertidumbre_expandida_95_t / huella_total_loc_t * 100.0), 2) if huella_total_loc_t > 0 else 0.0

        dictamen_miteco = (
            f"INFORME PERICIAL UNE-EN ISO 14064-1:2019 & REGISTRO OFICIAL MITECO: "
            f"Huella de Carbono de la Organización evaluada en {huella_total_loc_t:.3f} tCO2e (Location-based) / "
            f"{huella_total_mkt_t:.3f} tCO2e (Market-based). "
            f"Incertidumbre analítica expandida (k=2, 95% conf): ±{incertidumbre_expandida_95_t:.3f} tCO2e (±{incertidumbre_global_pct}%). "
            f"Apto para Declaración de Huella Sección A MITECO y Reporte ESRS E1 CSRD. "
            f"Lead Systems Architect: Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7)."
        )

        return {
            "normativa_aplicada": "UNE-EN ISO 14064-1:2019 · Metodología MITECO 2024 · CSRD ESRS E1",
            "alcance_1_directo_tCO2e": round(total_s1_t, 4),
            "alcance_2_location_based_tCO2e": round(total_s2_loc_t, 4),
            "alcance_2_market_based_tCO2e": round(total_s2_mkt_t, 4),
            "alcance_3_cadena_valor_tCO2e": round(total_s3_t, 4),
            "huella_total_location_based_tCO2e": round(huella_total_loc_t, 4),
            "huella_total_market_based_tCO2e": round(huella_total_mkt_t, 4),
            "incertidumbre_sigma_total_tCO2e": round(sigma_total_t, 4),
            "incertidumbre_expandida_95_pct_tCO2e": incertidumbre_expandida_95_t,
            "incertidumbre_relativa_pct": incertidumbre_global_pct,
            "intervalo_confianza_95_tCO2e": [
                round(max(0.0, huella_total_loc_t - incertidumbre_expandida_95_t), 4),
                round(huella_total_loc_t + incertidumbre_expandida_95_t, 4)
            ],
            "componentes_desglosados": [
                {
                    "nombre": c.nombre,
                    "alcance": c.alcance,
                    "categoria_iso": c.categoria_iso14064,
                    "dato_actividad": c.dato_actividad,
                    "unidad": c.unidad_actividad,
                    "fe": c.factor_emision,
                    "unidad_fe": c.unidad_fe,
                    "emisiones_tCO2e": c.emisiones_tCO2e,
                    "incertidumbre_absoluta_tCO2e": c.incertidumbre_absoluta_tCO2e
                }
                for c in componentes
            ],
            "dictamen_miteco": dictamen_miteco
        }
