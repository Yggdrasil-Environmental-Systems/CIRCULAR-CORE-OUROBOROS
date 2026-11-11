"""
TEST SUITE: CLASIFICADOR LER MITECO 2021 & CALIDAD BIORRESIDUOS LIFE-BIOBEST
=============================================================================
Pruebas unitarias de determinación de peligrosidad HP1-HP15 y evaluación agronómica.
"""

import unittest
from core.clasificador_ler_miteco import (
    ClasificadorLERMiteco,
    ConcentracionSustancia,
    PARES_ESPEJO_HABITUALES
)
from core.control_calidad_biorresiduos_biobest import (
    EvaluadorCalidadBiorresiduosBiobest,
    EnsayoCompost
)


class TestClasificadorLERMiteco(unittest.TestCase):
    """Batería de pruebas de clasificación LER y características de peligrosidad."""

    def test_evaluacion_hp7_carcinogeno_positivo(self):
        """Sustancia carcinógena H350 con concentración >= 0.1% debe activar HP7."""
        sustancias = [
            ConcentracionSustancia(nombre="Benzo[a]pireno", codigo_indicacion_peligro="H350", concentracion_pct=0.15)
        ]
        res = ClasificadorLERMiteco.evaluar_hp7_carcinogeno(sustancias)
        self.assertTrue(res.es_peligroso)
        self.assertEqual(res.hp_id, "HP 7")

    def test_evaluacion_hp7_carcinogeno_negativo(self):
        """Sustancia carcinógena H350 con concentración < 0.1% no debe activar HP7."""
        sustancias = [
            ConcentracionSustancia(nombre="Trazas HAP", codigo_indicacion_peligro="H350", concentracion_pct=0.04)
        ]
        res = ClasificadorLERMiteco.evaluar_hp7_carcinogeno(sustancias)
        self.assertFalse(res.es_peligroso)

    def test_evaluacion_hp14_ecotoxico_ue2017_997_positivo(self):
        """Ecuación ponderada crónica: 100*c(H410) + 10*c(H411) + c(H412) >= 25%."""
        sustancias = [
            ConcentracionSustancia(nombre="Biocida acuático", codigo_indicacion_peligro="H410", concentracion_pct=0.35)
        ]
        # 100 * 0.35 = 35.0 >= 25.0
        res = ClasificadorLERMiteco.evaluar_hp14_ecotoxico_ue2017_997(sustancias)
        self.assertTrue(res.es_peligroso)
        self.assertEqual(res.hp_id, "HP 14")

    def test_evaluacion_hp14_ecotoxico_ue2017_997_negativo(self):
        """Concentración ponderada por debajo del umbral del 25%."""
        sustancias = [
            ConcentracionSustancia(nombre="Sal mineral", codigo_indicacion_peligro="H412", concentracion_pct=5.0)
        ]
        res = ClasificadorLERMiteco.evaluar_hp14_ecotoxico_ue2017_997(sustancias)
        self.assertFalse(res.es_peligroso)

    def test_clasificacion_residuo_espejo_tierras_rcd_peligroso(self):
        """Tierra 17 05 04 con hidrocarburos carcinógenos debe derivar a 17 05 03*."""
        sustancias = [
            ConcentracionSustancia(nombre="HAP Fracción Pesada", codigo_indicacion_peligro="H350", concentracion_pct=0.25)
        ]
        res = ClasificadorLERMiteco.clasificar_residuo_espejo(
            codigo_propuesto="17 05 04",
            sustancias_analizadas=sustancias
        )
        self.assertTrue(res["es_peligroso"])
        self.assertEqual(res["codigo_ler_asignado"], "17 05 03*")
        self.assertIn("HP 7", res["hps_positivas"])

    def test_clasificacion_residuo_espejo_tierras_rcd_limpio(self):
        """Tierra 17 05 04 limpia debe confirmarse como no peligrosa."""
        sustancias = [
            ConcentracionSustancia(nombre="Carbonato cálcico", codigo_indicacion_peligro="", concentracion_pct=99.0)
        ]
        res = ClasificadorLERMiteco.clasificar_residuo_espejo(
            codigo_propuesto="17 05 04",
            sustancias_analizadas=sustancias
        )
        self.assertFalse(res["es_peligroso"])
        self.assertEqual(res["codigo_ler_asignado"], "17 05 04")
        self.assertEqual(len(res["hps_positivas"]), 0)


class TestControlCalidadBiorresiduosBiobest(unittest.TestCase):
    """Batería de pruebas de evaluación de compost según LIFE-BIOBEST y RD 506/2013."""

    def test_ratio_cn_maduro(self):
        """Compost con C/N entre 10 y 20 se clasifica como maduro óptimo."""
        res = EvaluadorCalidadBiorresiduosBiobest.evaluar_relacion_carbono_nitrogeno(c_pct=28.0, n_pct=1.8)
        self.assertTrue(res["apto_madurez"])
        self.assertAlmostEqual(res["ratio_cn"], 15.56, places=1)

    def test_ratio_cn_inmaduro(self):
        """Compost con exceso de carbono (C/N > 25) bloquea nitrógeno."""
        res = EvaluadorCalidadBiorresiduosBiobest.evaluar_relacion_carbono_nitrogeno(c_pct=45.0, n_pct=1.0)
        self.assertFalse(res["apto_madurez"])
        self.assertEqual(res["ratio_cn"], 45.0)

    def test_impurezas_life_biobest_conforme(self):
        """Impurezas totales <= 0.5% cumplen el estándar europeo LIFE-BIOBEST."""
        res = EvaluadorCalidadBiorresiduosBiobest.evaluar_impurezas_inertes(plasticos_pct=0.15, vidrios_metales_pct=0.10)
        self.assertTrue(res["conforme_life_biobest"])
        self.assertAlmostEqual(res["impurezas_totales_pct_ms"], 0.25, places=2)

    def test_impurezas_life_biobest_no_conforme(self):
        """Impurezas totales > 0.5% son rechazadas."""
        res = EvaluadorCalidadBiorresiduosBiobest.evaluar_impurezas_inertes(plasticos_pct=0.45, vidrios_metales_pct=0.20)
        self.assertFalse(res["conforme_life_biobest"])
        self.assertAlmostEqual(res["impurezas_totales_pct_ms"], 0.65, places=2)

    def test_clasificacion_metales_clase_a(self):
        """Compost con todos los metales bajo los límites de Clase A."""
        metales = {
            "cadmio_Cd": 0.4,
            "cobre_Cu": 50.0,
            "niquel_Ni": 18.0,
            "plomo_Pb": 30.0,
            "zinc_Zn": 150.0,
            "mercurio_Hg": 0.2,
            "cromo_total_Cr": 40.0
        }
        res = EvaluadorCalidadBiorresiduosBiobest.clasificar_metales_pesados_rd506(metales)
        self.assertEqual(res["clase_fertilizante_final"], "Clase A")
        self.assertTrue(res["apto_agricultura_ecologica"])

    def test_auditoria_completa_lote_compost_apto(self):
        """Auditoría de lote de compost conforme en todos los parámetros."""
        ensayo = EnsayoCompost(
            lote_id="LOTE-BIOBEST-2026-VAL",
            materia_organica_pct_ms=48.5,
            humedad_pct=35.0,
            carbono_organico_pct_ms=25.0,
            nitrogeno_total_pct_ms=1.7,
            impurezas_plasticos_pct_ms=0.12,
            impurezas_vidrio_metales_pct_ms=0.08,
            metales_pesados_mg_kg_ms={
                "cadmio_Cd": 0.35, "cobre_Cu": 45.0, "niquel_Ni": 15.0,
                "plomo_Pb": 25.0, "zinc_Zn": 140.0, "mercurio_Hg": 0.15, "cromo_total_Cr": 35.0
            },
            tasa_respiratoria_at4_mgO2_gSV=5.2,
            indice_germinacion_zucconi_pct=92.0
        )
        audit = EvaluadorCalidadBiorresiduosBiobest.auditar_lote_compost(ensayo)
        self.assertTrue(audit["apto_comercializacion"])
        self.assertEqual(audit["clase_legal"], "Clase A")
        self.assertTrue(audit["conforme_life_biobest"])


if __name__ == "__main__":
    unittest.main()
