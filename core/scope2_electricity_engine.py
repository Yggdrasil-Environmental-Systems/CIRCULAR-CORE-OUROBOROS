"""
MOTOR DE EMISIONES INDIRECTAS POR ELECTRICIDAD: ALCANCE 2 (SCOPE 2 - GHG PROTOCOL)
Implementa la doble contabilidad mandatoria por GHG Protocol: Location-based vs. Market-based.
"""

from typing import Dict, Any


class MotorScope2:
    """Motor de cálculo de emisiones indirectas por consumo de energía eléctrica de la red."""

    def __init__(self, factores: Dict[str, Any]):
        self.factores = factores.get("scope_2_electricity", {})

    def calcular_alcance_2(self, consumo_kwh: float, pct_renovable_gdo: float = 0.0, factor_personalizado_kg_kwh: float = None) -> Dict[str, Any]:
        """
        Calcula las emisiones de Alcance 2 bajo los métodos Location-based y Market-based.
        """
        ef_location = factor_personalizado_kg_kwh or self.factores.get(
            "spain_peninsular_grid_location_based_kgCO2e_per_kWh", 0.185
        )
        ef_gdo = self.factores.get("market_based_certified_renewable_gdo_kgCO2e_per_kWh", 0.000)

        # 1. Location-based (refleja la intensidad media física de la red eléctrica geográfica)
        emisiones_location_kgCO2e = consumo_kwh * ef_location

        # 2. Market-based (refleja la contractualidad de compra de energía verde con GdOs)
        kwh_renovable = consumo_kwh * (pct_renovable_gdo / 100.0)
        kwh_no_renovable = consumo_kwh - kwh_renovable
        emisiones_market_kgCO2e = (kwh_renovable * ef_gdo) + (kwh_no_renovable * ef_location)

        ahorro_market_vs_location_kgCO2e = max(0.0, emisiones_location_kgCO2e - emisiones_market_kgCO2e)

        return {
            "consumo_anual_kWh": round(consumo_kwh, 2),
            "factor_location_based_kgCO2e_kWh": ef_location,
            "pct_energia_renovable_certificada_pct": round(pct_renovable_gdo, 1),
            "emisiones_location_based_kgCO2e": round(emisiones_location_kgCO2e, 2),
            "emisiones_location_based_tCO2e": round(emisiones_location_kgCO2e / 1000.0, 4),
            "emisiones_market_based_kgCO2e": round(emisiones_market_kgCO2e, 2),
            "emisiones_market_based_tCO2e": round(emisiones_market_kgCO2e / 1000.0, 4),
            "ahorro_gdo_tCO2e": round(ahorro_market_vs_location_kgCO2e / 1000.0, 4)
        }
