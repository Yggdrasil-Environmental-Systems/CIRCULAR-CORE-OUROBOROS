"""
Pruebas Unitarias para el Módulo de Envases Comerciales (RD 1055/2022 & OUROBOROS_SPECTRA)
"""

import unittest
from core.envases_rd1055_rap import (
    OuroborosSpectraNIR,
    CalculadorCuotasRAP,
    MotorBalanceMasaCerrado,
    CertificadorFinCondicionResiduoEoW,
    FIRMAS_ESPECTRALES_POLIMEROS
)


class TestEnvasesRD1055(unittest.TestCase):

    def test_clasificacion_espectral_puro_pet(self):
        # Muestra con el espectro de PET de referencia
        espectro_pet = FIRMAS_ESPECTRALES_POLIMEROS["PET"]["reflectancia_curva"]
        res = OuroborosSpectraNIR.clasificar_muestra_espectral(espectro_pet)
        self.assertEqual(res["polimero_identificado"], "PET")
        self.assertAlmostEqual(res["confianza_pct"], 100.0, places=1)
        self.assertFalse(res["es_multicapa_complejo"])
        self.assertTrue(res["admisible_reciclaje_mecanico"])

    def test_clasificacion_espectral_multicapa_evoh(self):
        espectro_multi = FIRMAS_ESPECTRALES_POLIMEROS["MULTICAPA_EVOH"]["reflectancia_curva"]
        res = OuroborosSpectraNIR.clasificar_muestra_espectral(espectro_multi)
        self.assertEqual(res["polimero_identificado"], "MULTICAPA_EVOH")
        self.assertTrue(res["es_multicapa_complejo"])
        self.assertFalse(res["admisible_reciclaje_mecanico"])

    def test_balance_masa_cerrado_conforme(self):
        # 10,000 kg entrada -> 8,500 kg recuperado + 1,000 kg rechazo + 400 kg humedad = 9,900 kg (1.0% error <= 1.5%)
        bal = MotorBalanceMasaCerrado.auditar_balance(
            lote_id="LOTE-2026-001",
            entradas_kg=10000.0,
            recuperado_kg=8500.0,
            merma_kg=400.0,
            rechazo_kg=1000.0,
            polimero="PEAD"
        )
        self.assertTrue(bal["conforme_tolerancia_1_5pct"])
        self.assertEqual(bal["error_balance_pct"], 1.0)
        self.assertEqual(bal["penalizacion_recargo_rap_pct"], 0.0)

    def test_balance_masa_cerrado_infraccion_mayor_1_5_pct(self):
        # 10,000 kg entrada -> 8,000 kg salidas contabilizadas (20% discrepancia >> 1.5%)
        bal = MotorBalanceMasaCerrado.auditar_balance(
            lote_id="LOTE-2026-002",
            entradas_kg=10000.0,
            recuperado_kg=7000.0,
            merma_kg=500.0,
            rechazo_kg=500.0,
            polimero="LDPE_FILM"
        )
        self.assertFalse(bal["conforme_tolerancia_1_5pct"])
        self.assertGreater(bal["error_balance_pct"], 1.50)
        self.assertEqual(bal["penalizacion_recargo_rap_pct"], 25.0)

    def test_cuotas_rap_ecomodulacion(self):
        # 5,000 kg de PEAD con 60% reciclado certificado UNE-EN 15343
        rap = CalculadorCuotasRAP.calcular_cuota_envase(
            tipo_polimero="PEAD",
            kilos_puestos_mercado=5000.0,
            pct_reciclado_certificado=60.0,
            es_monomaterial_reciclable=True
        )
        self.assertLess(rap["cuota_final_rap_eur"], rap["coste_bruto_eur"])
        self.assertEqual(rap["estado_modulacion"], "BONIFICADO")

    def test_certificacion_eow_granza_conforme(self):
        # Lote de 10,000 kg de PEAD conforme con UNE-EN 15344 e impurezas < 1.5%
        res = CertificadorFinCondicionResiduoEoW.certificar_lote_granza_reciclada(
            lote_id="GRANZA-PEAD-2026-001",
            polimero="PEAD",
            masa_lote_kg=10000.0,
            pureza_nir_pct=99.2,
            impurezas_no_polimericas_pct=0.85,
            humedad_pct=0.45,
            mfi_medido_g_10min=0.84,
            mfi_nominal_g_10min=0.80
        )
        self.assertTrue(res["fin_condicion_residuo_conforme"])
        self.assertTrue(res["exento_impuesto_plastico_ley7"])
        self.assertEqual(res["ahorro_fiscal_impuesto_plastico_eur"], 4500.0)
        self.assertIn("UNE-EN 15344", res["norma_une_especifica"])

    def test_certificacion_eow_granza_rechazada_por_impurezas(self):
        # Lote con impurezas del 2.3% (> 1.5% limite legal)
        res = CertificadorFinCondicionResiduoEoW.certificar_lote_granza_reciclada(
            lote_id="GRANZA-PET-2026-002",
            polimero="PET",
            masa_lote_kg=5000.0,
            pureza_nir_pct=98.8,
            impurezas_no_polimericas_pct=2.30,
            humedad_pct=0.50,
            mfi_medido_g_10min=28.0,
            mfi_nominal_g_10min=28.0
        )
        self.assertFalse(res["fin_condicion_residuo_conforme"])
        self.assertFalse(res["exento_impuesto_plastico_ley7"])
        self.assertEqual(res["ahorro_fiscal_impuesto_plastico_eur"], 0.0)
        self.assertTrue(any("1.50%" in m for m in res["motivos_no_conformidad"]))

    def test_certificacion_aridos_reciclados_eow(self):
        # 500 toneladas de áridos reciclados con 96.5% pétreo y 0.5% impropios
        arido = CertificadorFinCondicionResiduoEoW.certificar_aridos_reciclados_eow(
            lote_id="ARIDO-RCD-2026-VAL",
            masa_toneladas=500.0,
            contenido_hormigon_piedra_pct=96.5,
            impurezas_no_petreas_pct=0.5
        )
        self.assertTrue(arido["arido_reciclado_apto_eow"])
        self.assertEqual(arido["ahorro_canon_vertedero_eur"], 20000.0)


if __name__ == "__main__":
    unittest.main()
