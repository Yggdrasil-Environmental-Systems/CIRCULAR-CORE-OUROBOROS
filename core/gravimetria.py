"""
MOTOR GRAVIMÉTRICO FORENSE Y BALANCES DE MASA CIBERFÍSICOS
Calcula balances de masa, volumetría cilíndrica geométrica y eficiencias de llenado de consumibles.
"""

import math
from typing import Dict, List, Any


class MotorGravimetrico:
    """Motor matemático de cálculo gravimétrico, volumetría y balance de masa."""

    @staticmethod
    def calcular_balance_mensual(bio_kg: float, sharps_kg: float, common_kg: float) -> Dict[str, float]:
        """Calcula los totales de masa y ratios de peligrosidad."""
        peligrosos = bio_kg + sharps_kg
        totales = peligrosos + common_kg
        ratio_biorriesgo = (peligrosos / totales * 100.0) if totales > 0 else 0.0
        return {
            "peligrosos_kg": round(peligrosos, 2),
            "comunes_kg": round(common_kg, 2),
            "totales_kg": round(totales, 2),
            "ratio_biorriesgo_pct": round(ratio_biorriesgo, 2)
        }

    @staticmethod
    def calcular_eficiencia_bolsa(masa_kg: float, numero_bolsas: int, capacidad_nominal_litros: float = 50.0) -> Dict[str, Any]:
        """
        Determina la eficiencia de carga real de las bolsas plásticas.
        Una bolsa de polietileno virgen HDPE de 50L (61x74 cm, galga 50 um) pesa ~28 gramos.
        """
        if numero_bolsas <= 0:
            return {"gramos_por_bolsa": 0.0, "tasa_subutilizacion_pct": 100.0, "alerta_anomalia": False}

        gramos_por_bolsa = (masa_kg * 1000.0) / numero_bolsas
        peso_polimero_virgen_bolsa_g = 28.0
        ratio_polimero_vs_residuo = (peso_polimero_virgen_bolsa_g / gramos_por_bolsa) if gramos_por_bolsa > 0 else 1.0

        # Capacidad estimada de diseño de una bolsa de 50L para residuos no compactados: ~10.000 g
        capacidad_referencia_g = 10000.0
        tasa_subutilizacion = max(0.0, (1.0 - (gramos_por_bolsa / capacidad_referencia_g)) * 100.0)

        # Alerta si el plástico virgen pesa más del 40% del residuo contenido
        alerta_anomalia = gramos_por_bolsa < 70.0

        return {
            "gramos_utiles_por_bolsa": round(gramos_por_bolsa, 2),
            "peso_propio_bolsa_g": peso_polimero_virgen_bolsa_g,
            "ratio_plastico_vs_residuo": round(ratio_polimero_vs_residuo, 3),
            "tasa_subutilizacion_pct": round(tasa_subutilizacion, 1),
            "alerta_anomalia": alerta_anomalia
        }

    @staticmethod
    def calcular_volumen_cilindrico(diametro_m: float, altura_inicial_m: float, altura_final_m: float) -> float:
        """
        Calcula el volumen geométrico cilíndrico de llenado según metodología gravimétrica
        y volumétrica UNE-EN 12574 / Decreto 83/1999 CAM:
        V = pi * r^2 * delta_h
        """
        radio = diametro_m / 2.0
        delta_h = max(0.0, altura_final_m - altura_inicial_m)
        volumen_m3 = math.pi * (radio ** 2) * delta_h
        return round(volumen_m3, 6)

    @staticmethod
    def descomposicion_sobresegregacion_aseos(servicios: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aísla la carga de biorriesgo procedente de aseos frente a áreas asistenciales clínicas directas.
        """
        total_bio_dia = 0.0
        bio_aseos_dia = 0.0
        bio_clinico_dia = 0.0

        for s in servicios:
            bio = s.get("bio_kg_day", 0.0)
            total_bio_dia += bio
            tipo = s.get("area_type", "").lower()
            nombre = s.get("name", "").lower()

            if "higiénico" in tipo or "higiénico" in nombre or "ss.hh." in nombre or "baño" in nombre:
                bio_aseos_dia += bio
            else:
                bio_clinico_dia += bio

        pct_aseos = (bio_aseos_dia / total_bio_dia * 100.0) if total_bio_dia > 0 else 0.0
        pct_clinico = (bio_clinico_dia / total_bio_dia * 100.0) if total_bio_dia > 0 else 0.0

        return {
            "total_bio_kg_dia": round(total_bio_dia, 3),
            "bio_aseos_kg_dia": round(bio_aseos_dia, 3),
            "bio_clinico_kg_dia": round(bio_clinico_dia, 3),
            "pct_biorriesgo_en_aseos": round(pct_aseos, 2),
            "pct_biorriesgo_clinico_real": round(pct_clinico, 2),
            "diagnostico_distorsion": pct_aseos > 70.0
        }
