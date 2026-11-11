"""
TEST SUITE: MOTOR DE HUELLA DE CARBONO UNE-EN ISO 14064-1:2019
==============================================================
Pruebas unitarias de inventario de GEI, propagación de incertidumbre gaussiana y metodología MITECO.
"""

import unittest
import json
from pathlib import Path
from core.huella_carbono_iso14064 import MotorHuellaCarbonoISO14064


class TestMotorHuellaCarbonoISO14064(unittest.TestCase):
    """Batería de pruebas de cálculo y verificación ISO 14064-1:2019."""

    @classmethod
    def setUpClass(cls):
        cfg_path = Path(__file__).resolve().parent.parent / "configs" / "factores_emision_oficiales.json"
        if cfg_path.exists():
            with open(cfg_path, "r", encoding="utf-8") as f:
                cls.factores = json.load(f)
        else:
            cls.factores = {}
        cls.motor = MotorHuellaCarbonoISO14064(cls.factores)

    def test_cuantificacion_inventario_basico(self):
        """Calcula inventario completo con Alcance 1, 2 y 3."""
        inv = self.motor.cuantificar_inventario(
            diesel_calefaccion_litros=1000.0,
            diesel_flota_vehiculos_litros=500.0,
            gas_natural_kwh=10000.0,
            gas_refrigerante_tipo="R-410A",
            refrigerante_recargado_kg=2.0,
            electricidad_red_kwh=50000.0,
            electricidad_gdo_renovable_pct=0.0,
            residuos_incineracion_t=1.5,
            residuos_autoclave_t=2.0,
            residuos_vertedero_t=5.0,
            residuos_reciclados_t=3.0,
            transporte_tkm=1200.0
        )

        self.assertGreater(inv["alcance_1_directo_tCO2e"], 0.0)
        self.assertGreater(inv["alcance_2_location_based_tCO2e"], 0.0)
        self.assertGreater(inv["huella_total_location_based_tCO2e"], 0.0)
        self.assertIn("UNE-EN ISO 14064-1:2019", inv["normativa_aplicada"])
        self.assertIn("Kelvin Jesús Flores Yarihuaman", inv["dictamen_miteco"])

    def test_propagacion_incertidumbre_gaussiana(self):
        """Verifica que la incertidumbre total siga la regla sigma_total = sqrt(sum sigma_i^2)."""
        inv = self.motor.cuantificar_inventario(
            diesel_calefaccion_litros=2000.0,
            gas_natural_kwh=20000.0,
            electricidad_red_kwh=30000.0
        )

        sigma = inv["incertidumbre_sigma_total_tCO2e"]
        u95 = inv["incertidumbre_expandida_95_pct_tCO2e"]
        self.assertGreater(sigma, 0.0)
        self.assertAlmostEqual(u95, round(1.96 * sigma, 4), places=3)
        self.assertGreaterEqual(inv["intervalo_confianza_95_tCO2e"][0], 0.0)
        self.assertGreater(inv["intervalo_confianza_95_tCO2e"][1], inv["huella_total_location_based_tCO2e"])

    def test_enfoque_mercado_con_garantias_origen(self):
        """Al 100% de Garantías de Origen Renovable, las emisiones de Alcance 2 Market-based deben ser 0."""
        inv = self.motor.cuantificar_inventario(
            electricidad_red_kwh=25000.0,
            electricidad_gdo_renovable_pct=100.0
        )
        self.assertEqual(inv["alcance_2_market_based_tCO2e"], 0.0)
        self.assertGreater(inv["alcance_2_location_based_tCO2e"], 0.0)

    def test_evitacion_emisiones_reciclaje_mecanico(self):
        """El reciclaje mecánico debe computar como evitación neta (emisión negativa en Cat 4)."""
        inv = self.motor.cuantificar_inventario(
            residuos_reciclados_t=10.0
        )
        comp_rec = [c for c in inv["componentes_desglosados"] if "Reciclaje Mecánico" in c["nombre"]]
        self.assertEqual(len(comp_rec), 1)
        self.assertLess(comp_rec[0]["emisiones_tCO2e"], 0.0)

    def test_integracion_scope3_a_iso14064_y_transporte_tkm(self):
        """Verifica que MotorScope3 exporte las toneladas y t·km requeridos por MotorHuellaCarbonoISO14064."""
        from core.scope3_waste_engine import MotorScope3
        s3_engine = MotorScope3(self.factores)
        s3_res = s3_engine.calcular_escenario_completo(
            peligroso_kg=305.27,
            comun_kg=3196.64,
            km_peligroso=65.0,
            km_comun=35.0,
            tecnologia_peligroso="autoclave_esterilizacion_vapor",
            pct_reciclaje_comun=30.0
        )
        self.assertIn("autoclave_t", s3_res)
        self.assertIn("vertedero_t", s3_res)
        self.assertIn("reciclaje_t", s3_res)
        self.assertIn("transporte_tkm", s3_res)
        self.assertGreater(s3_res["autoclave_t"], 0.30)
        self.assertGreater(s3_res["transporte_tkm"], 100.0)

        inv = self.motor.cuantificar_inventario(
            electricidad_red_kwh=74500.0,
            residuos_incineracion_t=s3_res["incineracion_t"],
            residuos_autoclave_t=s3_res["autoclave_t"],
            residuos_vertedero_t=s3_res["vertedero_t"],
            residuos_reciclados_t=s3_res["reciclaje_t"],
            transporte_tkm=s3_res["transporte_tkm"]
        )
        self.assertNotEqual(inv["alcance_3_cadena_valor_tCO2e"], 0.0)
        comp_tkm = [c for c in inv["componentes_desglosados"] if "t·km" in c["nombre"]]
        self.assertEqual(len(comp_tkm), 1)
        self.assertGreater(comp_tkm[0]["emisiones_tCO2e"], 0.0)

    def test_integridad_boveda_athena_y_aduana_astraea_y_separacion_opencore(self):
        """Verifica el sellado SHA-256 de scientific_dna.json, regulatory_dna.json y el paquete Open-Core."""
        from physics.sentinel_sidecar import PhysicsSentinelSidecar
        from compliance.auto_verificador_integridad import verificar_integridad_core

        sentinel = PhysicsSentinelSidecar()
        self.assertTrue(sentinel.is_valid)
        self.assertGreaterEqual(len(sentinel.dna.get("papers_seminales_seleccionados", [])), 12)
        for p in sentinel.dna.get("papers_seminales_seleccionados", []):
            self.assertNotIn("MINAM", p["archivo"].upper())
            self.assertNotIn("UCSS", p["archivo"].upper())

        diag = verificar_integridad_core()
        self.assertEqual(diag["estado"], "CERTIFICADO_CONFORME_MECES3")
        self.assertTrue(diag["dna_integro"])

        hf_app = Path(__file__).resolve().parent.parent / "huggingface_space" / "app.py"
        self.assertTrue(hf_app.exists())
        hf_code = hf_app.read_text(encoding="utf-8")
        self.assertNotIn("from enterprise", hf_code)
        self.assertNotIn("from reporting", hf_code)


if __name__ == "__main__":
    unittest.main()
