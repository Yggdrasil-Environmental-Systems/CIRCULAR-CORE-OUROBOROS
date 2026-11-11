"""
MOTOR DE DESCARBONIZACIÓN DE CADENA DE VALOR: ALCANCE 3 (SCOPE 3 - CATEGORÍA 5, 4/9 Y 1)
Implementa el cálculo con datos de actividad primaria (Waste-Type-Specific Method) y vector logístico rodado (t·km).
"""

from typing import Dict, Any


class MotorScope3:
    """Motor de cálculo de emisiones de Alcance 3 para gestión de residuos, logística y polímeros fungibles."""

    def __init__(self, factores: Dict[str, Any]):
        self.factores = factores.get("scope_3_value_chain", {})

    def calcular_transporte_tkm(self, masa_kg: float, distancia_km: float, tipo_vehiculo: str = "camion_rigido_diesel_pesado") -> Dict[str, float]:
        """Calcula las emisiones del transporte rodado mediante el indicador tonelada-kilómetro."""
        toneladas = masa_kg / 1000.0
        tkm = toneladas * distancia_km
        ef_tkm = self.factores.get("category_4_9_transport_kgCO2e_per_tkm", {}).get(tipo_vehiculo, 0.190)
        emisiones_kgCO2e = tkm * ef_tkm
        return {
            "toneladas": round(toneladas, 4),
            "distancia_km": round(distancia_km, 2),
            "toneladas_kilometro": round(tkm, 3),
            "factor_emision_tkm": ef_tkm,
            "emisiones_transporte_kgCO2e": round(emisiones_kgCO2e, 3)
        }

    def calcular_tratamiento_fin_de_vida(self, peligroso_kg: float, comun_kg: float, tecnologia_peligroso: str = "incineracion_termica_1200C", pct_reciclaje_comun: float = 0.0) -> Dict[str, Any]:
        """
        Calcula las emisiones de tratamiento final de residuos.
        Soporta incineración a 1.200 °C, autoclave a vapor, vertedero controlado y créditos de reciclaje mecánico.
        """
        efs = self.factores.get("category_5_waste_treatment_kgCO2e_per_kg", {
            "incineracion_termica_1200C": 1.800,
            "autoclave_esterilizacion_vapor": 0.220,
            "vertedero_controlado_fraccion_resto": 0.580,
            "reciclaje_mecanico_evitacion_neta": -0.700
        })

        ef_peligroso = efs.get(tecnologia_peligroso, 1.800)
        ef_vertedero = efs.get("vertedero_controlado_fraccion_resto", 0.580)
        ef_reciclaje = efs.get("reciclaje_mecanico_evitacion_neta", -0.700)

        # Emisión de fracción peligrosa
        emision_peligroso = peligroso_kg * ef_peligroso

        # Emisión de fracción común con desvío a economía circular
        kg_reciclado = comun_kg * (pct_reciclaje_comun / 100.0)
        kg_vertedero = comun_kg - kg_reciclado

        emision_vertedero = kg_vertedero * ef_vertedero
        credito_reciclaje = kg_reciclado * ef_reciclaje
        emision_comun_neta = emision_vertedero + credito_reciclaje

        total_tratamiento_kgCO2e = emision_peligroso + emision_comun_neta

        return {
            "peligrosos_kg": round(peligroso_kg, 2),
            "tecnologia_peligroso": tecnologia_peligroso,
            "emision_peligrosos_kgCO2e": round(emision_peligroso, 2),
            "comunes_vertedero_kg": round(kg_vertedero, 2),
            "comunes_reciclaje_kg": round(kg_reciclado, 2),
            "emision_vertedero_kgCO2e": round(emision_vertedero, 2),
            "credito_reciclaje_evitado_kgCO2e": round(credito_reciclaje, 2),
            "emision_comunes_neta_kgCO2e": round(emision_comun_neta, 2),
            "total_tratamiento_kgCO2e": round(total_tratamiento_kgCO2e, 2),
            "total_tratamiento_tCO2e": round(total_tratamiento_kgCO2e / 1000.0, 4)
        }

    def calcular_huella_bolsas_virgen(self, numero_bolsas_rojas: int, numero_bolsas_negras: int, peso_bolsa_g: float = 28.0) -> Dict[str, float]:
        """Calcula la huella de carbono de Alcance 3 Cat. 1 por fabricación del polímero plástico virgen consumido."""
        total_bolsas = numero_bolsas_rojas + numero_bolsas_negras
        masa_plastico_kg = (total_bolsas * peso_bolsa_g) / 1000.0
        ef_hdpe = self.factores.get("category_1_purchased_goods_kgCO2e_per_kg", {}).get("polietileno_alta_densidad_virgen_hdpe", 2.100)
        emisiones_bolsas_kgCO2e = masa_plastico_kg * ef_hdpe

        return {
            "total_bolsas_consumidas": total_bolsas,
            "masa_polimero_virgen_kg": round(masa_plastico_kg, 2),
            "emisiones_fabricacion_bolsas_kgCO2e": round(emisiones_bolsas_kgCO2e, 2),
            "emisiones_fabricacion_bolsas_tCO2e": round(emisiones_bolsas_kgCO2e / 1000.0, 4)
        }

    def calcular_escenario_completo(self, peligroso_kg: float, comun_kg: float, km_peligroso: float, km_comun: float, tecnologia_peligroso: str = "incineracion_termica_1200C", pct_reciclaje_comun: float = 0.0) -> Dict[str, Any]:
        """Calcula el balance global de Alcance 3 sumando logística rodada y tratamiento."""
        trans_p = self.calcular_transporte_tkm(peligroso_kg, km_peligroso)
        trans_c = self.calcular_transporte_tkm(comun_kg, km_comun)
        total_trans_kgCO2e = trans_p["emisiones_transporte_kgCO2e"] + trans_c["emisiones_transporte_kgCO2e"]

        trat = self.calcular_tratamiento_fin_de_vida(peligroso_kg, comun_kg, tecnologia_peligroso, pct_reciclaje_comun)
        total_alcance_3_kgCO2e = total_trans_kgCO2e + trat["total_tratamiento_kgCO2e"]

        es_autoclave = "autoclave" in tecnologia_peligroso.lower()
        incin_t = 0.0 if es_autoclave else (peligroso_kg / 1000.0)
        autoc_t = (peligroso_kg / 1000.0) if es_autoclave else 0.0
        vert_t = trat["comunes_vertedero_kg"] / 1000.0
        recic_t = trat["comunes_reciclaje_kg"] / 1000.0
        total_tkm = trans_p["toneladas_kilometro"] + trans_c["toneladas_kilometro"]

        return {
            "transporte_peligrosos": trans_p,
            "transporte_comunes": trans_c,
            "total_transporte_kgCO2e": round(total_trans_kgCO2e, 2),
            "tratamiento": trat,
            "incineracion_t": round(incin_t, 6),
            "autoclave_t": round(autoc_t, 6),
            "vertedero_t": round(vert_t, 6),
            "reciclaje_t": round(recic_t, 6),
            "transporte_tkm": round(total_tkm, 3),
            "total_scope_3_kgCO2e": round(total_alcance_3_kgCO2e, 2),
            "total_scope_3_tCO2e": round(total_alcance_3_kgCO2e / 1000.0, 4)
        }
