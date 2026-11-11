"""
CONTROL DE CALIDAD DE BIORRESIDUOS Y COMPOST (LIFE-BIOBEST 2024 & LEY 7/2022)
=============================================================================
Conforme a:
- Proyecto Europeo LIFE-BIOBEST (2024) - Directrices de Calidad de Compost y Digestato
- Ley 7/2022, de 8 de abril, de residuos y suelos contaminados (Art. 28 Biorresiduos)
- Real Decreto 1051/2022 (Nutrición sostenible en suelos agrícolas)
- Real Decreto 506/2013, de 28 de junio, sobre productos fertilizantes (Clases A, B y C)
- Norma UNE-EN 16086 / UNE-EN 16087 (Muestreo y caracterización de enmiendas orgánicas)

Autor: Kelvin Jesús Flores Yarihuaman | Lead Systems Architect (MECES 3 / EQF 7)
Ecosistema: Yggdrasil Environmental Systems · CIRCULAR-CORE: OUROBOROS (0x05)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


# Límites oficiales de metales pesados en mg/kg de materia seca (RD 506/2013 y LIFE-BIOBEST)
LIMITES_METALES_PESADOS_MG_KG_MS = {
    "cadmio_Cd": {"clase_A": 0.7, "clase_B": 2.0, "clase_C": 3.0},
    "cobre_Cu": {"clase_A": 70.0, "clase_B": 300.0, "clase_C": 400.0},
    "niquel_Ni": {"clase_A": 25.0, "clase_B": 90.0, "clase_C": 100.0},
    "plomo_Pb": {"clase_A": 45.0, "clase_B": 150.0, "clase_C": 200.0},
    "zinc_Zn": {"clase_A": 200.0, "clase_B": 500.0, "clase_C": 1000.0},
    "mercurio_Hg": {"clase_A": 0.4, "clase_B": 1.5, "clase_C": 2.5},
    "cromo_total_Cr": {"clase_A": 70.0, "clase_B": 250.0, "clase_C": 300.0}
}


@dataclass
class EnsayoCompost:
    """Parámetros de laboratorio de un lote de compost/digestato."""
    lote_id: str
    materia_organica_pct_ms: float  # Materia orgánica s/m.s. (mínimo 35-40%)
    humedad_pct: float  # Humedad (óptimo 30-45%)
    carbono_organico_pct_ms: float
    nitrogeno_total_pct_ms: float
    impurezas_plasticos_pct_ms: float  # Límite LIFE-BIOBEST < 0.3%
    impurezas_vidrio_metales_pct_ms: float  # Límite LIFE-BIOBEST < 0.2%
    metales_pesados_mg_kg_ms: Dict[str, float]
    tasa_respiratoria_at4_mgO2_gSV: float  # Índice AT4 (madurez < 10 mg O2/g SV)
    indice_germinacion_zucconi_pct: float = 85.0  # Fitotoxicidad (> 80% no fitotóxico)


class EvaluadorCalidadBiorresiduosBiobest:
    """
    Evaluador determinista de aptitud agronómica, pureza física y categorización legal
    de compost conforme al marco europeo LIFE-BIOBEST 2024 y RD 506/2013 / RD 1051/2022.
    """

    LIMITE_MAX_IMPUREZAS_TOTALES_LIFE_BIOBEST_PCT = 0.50  # < 0.5% en masa seca

    @classmethod
    def evaluar_relacion_carbono_nitrogeno(cls, c_pct: float, n_pct: float) -> Dict[str, Any]:
        """Calcula y evalúa la relación estequiométrica C/N del compost."""
        if n_pct <= 0:
            return {"ratio_cn": 0.0, "diagnostico": "INVÁLIDO (Nitrógeno nulo)", "apto_madurez": False}

        ratio = round(c_pct / n_pct, 2)
        if ratio < 10.0:
            diag = "Sobre-mineralizado (riesgo de emisión amoniacal en suelo)"
            maduro = True
        elif 10.0 <= ratio <= 20.0:
            diag = "Compost Maduro Óptimo (estabilizado y asimilable)"
            maduro = True
        elif 20.0 < ratio <= 30.0:
            diag = "En fase de maduración (ligeramente inmaduro)"
            maduro = False
        else:
            diag = "Inmaduro / Bloqueo de Nitrógeno (inmovilización de N en cultivo)"
            maduro = False

        return {
            "ratio_cn": ratio,
            "diagnostico": diag,
            "apto_madurez": maduro,
            "rango_optimo_compost_final": "10:1 - 20:1"
        }

    @classmethod
    def evaluar_impurezas_inertes(cls, plasticos_pct: float, vidrios_metales_pct: float) -> Dict[str, Any]:
        """Evalúa las impurezas físicas macroscópicas según estándar estricto LIFE-BIOBEST (< 0.50%)."""
        total_impurezas = round(plasticos_pct + vidrios_metales_pct, 3)
        cumple = total_impurezas <= cls.LIMITE_MAX_IMPUREZAS_TOTALES_LIFE_BIOBEST_PCT

        return {
            "impurezas_plasticos_pct": plasticos_pct,
            "impurezas_vidrio_metales_pct": vidrios_metales_pct,
            "impurezas_totales_pct_ms": total_impurezas,
            "limite_max_biobest_pct": cls.LIMITE_MAX_IMPUREZAS_TOTALES_LIFE_BIOBEST_PCT,
            "conforme_life_biobest": cumple,
            "dictamen_impurezas": (
                "CONFORME con estándares europeos LIFE-BIOBEST (< 0.5% m.s.)."
                if cumple else
                f"NO CONFORME: Exceso de impropios ({total_impurezas}% > 0.50%). Riesgo de contaminación por microplásticos."
            )
        }

    @classmethod
    def clasificar_metales_pesados_rd506(cls, metales: Dict[str, float]) -> Dict[str, Any]:
        """Clasifica el compost en Clase A (apto agricultura ecológica), Clase B o Clase C."""
        clasificacion = "Clase A"

        detalle_metales = {}
        for elemento, limites in LIMITES_METALES_PESADOS_MG_KG_MS.items():
            val = metales.get(elemento, 0.0)
            if val <= limites["clase_A"]:
                clase_elem = "Clase A"
            elif val <= limites["clase_B"]:
                clase_elem = "Clase B"
                if clasificacion == "Clase A":
                    clasificacion = "Clase B"
            elif val <= limites["clase_C"]:
                clase_elem = "Clase C"
                clasificacion = "Clase C"
            else:
                clase_elem = "NO CONFORME (Supera Clase C)"
                clasificacion = "NO CONFORME (Infracción Grave)"

            detalle_metales[elemento] = {
                "medido_mg_kg_ms": val,
                "limite_A": limites["clase_A"],
                "limite_B": limites["clase_B"],
                "clase": clase_elem
            }

        return {
            "clase_fertilizante_final": clasificacion,
            "apto_agricultura_ecologica": (clasificacion == "Clase A"),
            "apto_suelos_agricolas_rd1051": clasificacion in ["Clase A", "Clase B"],
            "detalle_elementos": detalle_metales
        }

    @classmethod
    def auditar_lote_compost(cls, ensayo: EnsayoCompost) -> Dict[str, Any]:
        """Auditoría pericial completa de calidad de lote de compost conforme a LIFE-BIOBEST y RD 506/2013."""
        eval_cn = cls.evaluar_relacion_carbono_nitrogeno(ensayo.carbono_organico_pct_ms, ensayo.nitrogeno_total_pct_ms)
        eval_impurezas = cls.evaluar_impurezas_inertes(ensayo.impurezas_plasticos_pct_ms, ensayo.impurezas_vidrio_metales_pct_ms)
        eval_metales = cls.clasificar_metales_pesados_rd506(ensayo.metales_pesados_mg_kg_ms)

        # Madurez biológica
        madurez_at4_ok = ensayo.tasa_respiratoria_at4_mgO2_gSV <= 10.0
        fitotoxicidad_ok = ensayo.indice_germinacion_zucconi_pct >= 80.0
        madurez_global = eval_cn["apto_madurez"] and madurez_at4_ok and fitotoxicidad_ok

        lote_apto_mercado = (
            eval_impurezas["conforme_life_biobest"] and
            eval_metales["apto_suelos_agricolas_rd1051"] and
            madurez_global
        )

        dictamen = (
            f"DICTAMEN PERICIAL CALIDAD BIORRESIDUOS (LIFE-BIOBEST 2024 / RD 506/2013): Lote '{ensayo.lote_id}' calificado como "
            f"{eval_metales['clase_fertilizante_final']} con {eval_impurezas['impurezas_totales_pct_ms']}% de impurezas macroscópicas y ratio C/N {eval_cn['ratio_cn']}. "
            f"Veredicto: {'APTO PARA COMERCIALIZACIÓN AGRÍCOLA' if lote_apto_mercado else 'NO CONFORME - REPROCESO O VALORIZACIÓN ENERGÉTICA REQUERIDA'}. "
            f"Director Técnico: Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7)."
        )

        return {
            "lote_id": ensayo.lote_id,
            "apto_comercializacion": lote_apto_mercado,
            "clase_legal": eval_metales["clase_fertilizante_final"],
            "ratio_cn": eval_cn["ratio_cn"],
            "madurez_biologica_at4_mgO2_gSV": ensayo.tasa_respiratoria_at4_mgO2_gSV,
            "indice_germinacion_pct": ensayo.indice_germinacion_zucconi_pct,
            "impurezas_inertes_pct": eval_impurezas["impurezas_totales_pct_ms"],
            "conforme_life_biobest": eval_impurezas["conforme_life_biobest"],
            "dictamen_pericial": dictamen,
            "eval_cn": eval_cn,
            "eval_impurezas": eval_impurezas,
            "eval_metales": eval_metales
        }
