"""
MOTOR DE EMISIONES DIRECTAS: ALCANCE 1 (SCOPE 1 - GHG PROTOCOL)
Calcula combustión estacionaria (grupos electrógenos y calderas) y fugas de gases fluorados refrigerantes HVAC (IPCC AR6).
"""

from typing import Dict, Any


class MotorScope1:
    """Motor de cálculo de emisiones directas de Alcance 1."""

    def __init__(self, factores: Dict[str, Any]):
        self.factores = factores.get("scope_1_direct", {})

    def calcular_emisiones_combustion(self, diesel_litros: float = 0.0, gas_natural_kwh: float = 0.0) -> Dict[str, float]:
        """Calcula emisiones por combustión fija in situ."""
        ef_diesel = self.factores.get("combustion_fuels", {}).get("diesel_heating_oil_kgCO2e_per_liter", 2.521)
        ef_gas = self.factores.get("combustion_fuels", {}).get("natural_gas_kgCO2e_per_kWh", 0.202)

        emisiones_diesel = diesel_litros * ef_diesel
        emisiones_gas = gas_natural_kwh * ef_gas
        total_kg = emisiones_diesel + emisiones_gas

        return {
            "diesel_kgCO2e": round(emisiones_diesel, 2),
            "gas_natural_kgCO2e": round(emisiones_gas, 2),
            "total_combustion_kgCO2e": round(total_kg, 2),
            "total_combustion_tCO2e": round(total_kg / 1000.0, 4)
        }

    def calcular_fugas_refrigerantes(self, tipo_gas: str, carga_kg: float, tasa_fuga_anual_pct: float = 3.5) -> Dict[str, Any]:
        """
        Calcula emisiones fugitivas por recarga o pérdida de refrigerantes en climatización.
        Utiliza los Potenciales de Calentamiento Global (GWP a 100 años) del IPCC Sexto Informe de Evaluación (AR6).
        """
        gwps = self.factores.get("refrigerant_fugitive_gwp_ar6", {
            "R-410A": 2088.0,
            "R-134a": 1430.0,
            "R-32": 675.0,
            "R-404A": 3922.0
        })

        gwp = gwps.get(tipo_gas.upper(), 2088.0)
        kg_fugados = carga_kg * (tasa_fuga_anual_pct / 100.0)
        emisiones_kgCO2e = kg_fugados * gwp

        return {
            "refrigerante": tipo_gas.upper(),
            "gwp_ipcc_ar6": gwp,
            "carga_total_kg": round(carga_kg, 2),
            "fuga_estimada_kg_ano": round(kg_fugados, 3),
            "emisiones_fugitivas_kgCO2e": round(emisiones_kgCO2e, 2),
            "emisiones_fugitivas_tCO2e": round(emisiones_kgCO2e / 1000.0, 4)
        }

    def calcular_alcance_1_total(self, diesel_litros: float, gas_kwh: float, tipo_refrigerante: str, carga_ref_kg: float, tasa_fuga_pct: float = 3.5) -> Dict[str, Any]:
        """Calcula el consolidado completo de Alcance 1."""
        comb = self.calcular_emisiones_combustion(diesel_litros, gas_kwh)
        fugas = self.calcular_fugas_refrigerantes(tipo_refrigerante, carga_ref_kg, tasa_fuga_pct)

        total_kg = comb["total_combustion_kgCO2e"] + fugas["emisiones_fugitivas_kgCO2e"]

        return {
            "combustion": comb,
            "fugas_refrigerantes": fugas,
            "total_scope_1_kgCO2e": round(total_kg, 2),
            "total_scope_1_tCO2e": round(total_kg / 1000.0, 4)
        }
