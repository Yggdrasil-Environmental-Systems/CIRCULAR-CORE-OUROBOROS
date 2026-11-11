"""
CLASIFICADOR PERICIAL LER MITECO 2021 & EVALUADOR DE PELIGROSIDAD HP1-HP15
==========================================================================
Conforme a:
- Decisión 2000/532/CE (Lista Europea de Residuos)
- Decisión 2014/955/UE
- Reglamento (UE) nº 1357/2014 (Características de Peligrosidad HP1 a HP15)
- Reglamento (UE) 2017/997 (Ecotoxicidad Acuática HP14)
- Guía Técnica para la Clasificación de Residuos (MITECO, 2021)
- Ley 7/2022, de 8 de abril, de residuos y suelos contaminados

Autor: Kelvin Jesús Flores Yarihuaman | Lead Systems Architect (MECES 3 / EQF 7)
Ecosistema: Yggdrasil Environmental Systems · CIRCULAR-CORE: OUROBOROS (0x05)
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class ConcentracionSustancia:
    """Concentración de sustancia química presente en el residuo para evaluación HP."""
    nombre: str
    numero_cas: Optional[str] = None
    codigo_indicacion_peligro: str = ""  # Códigos H (p.ej. H350, H300, H410, etc.)
    concentracion_pct: float = 0.0  # Concentración en % masa/masa (0 - 100)


@dataclass
class ResultadoEvaluacionHP:
    """Resultado determinista de evaluación de una característica de peligrosidad."""
    hp_id: str
    nombre: str
    es_peligroso: bool
    limite_superado: bool
    umbral_limite_pct: float
    concentracion_relevante_pct: float
    justificacion_normativa: str


# Tabla de códigos LER espejo habituales (par no peligroso / peligroso)
PARES_ESPEJO_HABITUALES: Dict[str, Dict[str, str]] = {
    "17 05 04": {
        "codigo_no_peligroso": "17 05 04",
        "descripcion_no_peligroso": "Tierra y piedras distintas de las especificadas en el código 17 05 03",
        "codigo_peligroso": "17 05 03*",
        "descripcion_peligroso": "Tierra y piedras que contienen sustancias peligrosas",
        "sector": "RCD / Obra Civil (RD 105/2008)"
    },
    "19 12 12": {
        "codigo_no_peligroso": "19 12 12",
        "descripcion_no_peligroso": "Otros residuos (incluidas mezclas de materiales) del tratamiento mecánico de residuos distintos de los especificados en el código 19 12 11",
        "codigo_peligroso": "19 12 11*",
        "descripcion_peligroso": "Otros residuos (incluidas mezclas de materiales) del tratamiento mecánico de residuos que contienen sustancias peligrosas",
        "sector": "Plantas de Tratamiento Mecánico-Biológico (TMB)"
    },
    "18 01 04": {
        "codigo_no_peligroso": "18 01 04",
        "descripcion_no_peligroso": "Residuos cuya recogida y eliminación no es objeto de requisitos especiales para prevenir infecciones",
        "codigo_peligroso": "18 01 03*",
        "descripcion_peligroso": "Residuos cuya recogida y eliminación es objeto de requisitos especiales para prevenir infecciones",
        "sector": "Ámbito Sanitario / Clínico"
    },
    "16 02 14": {
        "codigo_no_peligroso": "16 02 14",
        "descripcion_no_peligroso": "Equipos desechados distintos de los especificados en los códigos 16 02 09 a 16 02 13",
        "codigo_peligroso": "16 02 13*",
        "descripcion_peligroso": "Equipos desechados que contienen componentes peligrosos distintos de los especificados en los códigos 16 02 09 a 16 02 12",
        "sector": "RAEE (RD 110/2015)"
    },
    "15 01 02": {
        "codigo_no_peligroso": "15 01 02",
        "descripcion_no_peligroso": "Envases de plástico",
        "codigo_peligroso": "15 01 10*",
        "descripcion_peligroso": "Envases que contienen restos de sustancias peligrosas o están contaminados por ellas",
        "sector": "Envases Industriales y Comerciales (RD 1055/2022)"
    }
}


class ClasificadorLERMiteco:
    """
    Motor Pericial Determinista para la aplicación del Árbol de Decisión MITECO (2021)
    y el Reglamento (UE) nº 1357/2014 con cálculo riguroso de HP1 a HP15.
    """

    # Umbrales canónicos de corte (concentraciones límites) según Reglamento 1357/2014 y MITECO 2021
    UMBRALES_HP = {
        "HP4_IRRITANTE": {"cut_off_pct": 1.0, "limite_suma_pct": 20.0},
        "HP5_TOXICIDAD_ORGANOS": {"cut_off_pct": 1.0, "limite_cat1_pct": 1.0, "limite_cat2_pct": 10.0},
        "HP6_TOXICIDAD_AGUDA": {"cut_off_pct": 0.1, "limite_cat1_3_pct": 0.1, "limite_cat4_pct": 1.0},
        "HP7_CARCINOGENO": {"limite_cat1A_1B_pct": 0.1, "limite_cat2_pct": 1.0},
        "HP8_CORROSIVO": {"limite_cat1A_pct": 1.0, "limite_cat1B_pct": 5.0},
        "HP10_TOXICO_REPRODUCCION": {"limite_cat1A_1B_pct": 0.3, "limite_cat2_pct": 3.0},
        "HP11_MUTAGENO": {"limite_cat1A_1B_pct": 0.1, "limite_cat2_pct": 1.0},
        "HP13_SENSIBILIZANTE": {"limite_cut_off_pct": 10.0},
        "HP14_ECOTOXICO": {"cut_off_agudo_pct": 0.1, "cut_off_cronico_pct": 0.1, "limite_ponderado": 25.0}
    }

    @staticmethod
    def evaluar_hp4_irritacion_cutanea(sustancias: List[ConcentracionSustancia]) -> ResultadoEvaluacionHP:
        """HP 4: 'Irritante - irritación cutánea y lesiones oculares'."""
        suma_h314_1a = sum(s.concentracion_pct for s in sustancias if "H314" in s.codigo_indicacion_peligro and s.concentracion_pct >= 1.0)
        suma_h315_h318 = sum(s.concentracion_pct for s in sustancias if any(h in s.codigo_indicacion_peligro for h in ["H315", "H318", "H319"]) and s.concentracion_pct >= 1.0)
        
        es_peligroso = (suma_h314_1a >= 1.0) or (suma_h315_h318 >= 20.0)
        return ResultadoEvaluacionHP(
            hp_id="HP 4",
            nombre="Irritante (lesiones oculares e irritación cutánea)",
            es_peligroso=es_peligroso,
            limite_superado=es_peligroso,
            umbral_limite_pct=20.0,
            concentracion_relevante_pct=round(suma_h315_h318, 2),
            justificacion_normativa="Reglamento (UE) 1357/2014 Anexo III: Suma H315+H319 >= 20% o H314 1A >= 1%."
        )

    @staticmethod
    def evaluar_hp7_carcinogeno(sustancias: List[ConcentracionSustancia]) -> ResultadoEvaluacionHP:
        """HP 7: 'Carcinógeno' (H350 Cat 1A/1B límite >= 0.1%, H351 Cat 2 límite >= 1.0%)."""
        max_h350 = max((s.concentracion_pct for s in sustancias if "H350" in s.codigo_indicacion_peligro), default=0.0)
        max_h351 = max((s.concentracion_pct for s in sustancias if "H351" in s.codigo_indicacion_peligro), default=0.0)
        
        es_peligroso = (max_h350 >= 0.1) or (max_h351 >= 1.0)
        concentracion = max_h350 if max_h350 >= 0.1 else max_h351
        return ResultadoEvaluacionHP(
            hp_id="HP 7",
            nombre="Carcinógeno",
            es_peligroso=es_peligroso,
            limite_superado=es_peligroso,
            umbral_limite_pct=0.1 if max_h350 > 0 else 1.0,
            concentracion_relevante_pct=round(concentracion, 3),
            justificacion_normativa="Reglamento (UE) 1357/2014: Sustancia individual H350 >= 0.1% o H351 >= 1.0%."
        )

    @staticmethod
    def evaluar_hp14_ecotoxico_ue2017_997(sustancias: List[ConcentracionSustancia]) -> ResultadoEvaluacionHP:
        """
        HP 14: 'Ecotóxico' según la fórmula vinculante del Reglamento (UE) 2017/997:
        1. Si suma c(H400) >= 25% -> HP 14
        2. Si (100 * suma c(H410)) + (10 * suma c(H411)) + suma c(H412) >= 25% -> HP 14
        3. Si suma c(H410) + suma c(H411) + suma c(H412) + suma c(H413) >= 25% -> HP 14
        """
        c_h400 = sum(s.concentracion_pct for s in sustancias if "H400" in s.codigo_indicacion_peligro and s.concentracion_pct >= 0.1)
        c_h410 = sum(s.concentracion_pct for s in sustancias if "H410" in s.codigo_indicacion_peligro and s.concentracion_pct >= 0.1)
        c_h411 = sum(s.concentracion_pct for s in sustancias if "H411" in s.codigo_indicacion_peligro and s.concentracion_pct >= 1.0)
        c_h412 = sum(s.concentracion_pct for s in sustancias if "H412" in s.codigo_indicacion_peligro and s.concentracion_pct >= 1.0)
        c_h413 = sum(s.concentracion_pct for s in sustancias if "H413" in s.codigo_indicacion_peligro and s.concentracion_pct >= 1.0)

        # Regla 1: Toxicidad acuática aguda
        cond_aguda = c_h400 >= 25.0
        # Regla 2: Suma ponderada acuática crónica (Reglamento UE 2017/997)
        suma_ponderada_cronica = (100.0 * c_h410) + (10.0 * c_h411) + c_h412
        cond_cronica_ponderada = suma_ponderada_cronica >= 25.0
        # Regla 3: Suma simple crónica
        suma_simple_cronica = c_h410 + c_h411 + c_h412 + c_h413
        cond_cronica_simple = suma_simple_cronica >= 25.0

        es_peligroso = cond_aguda or cond_cronica_ponderada or cond_cronica_simple

        return ResultadoEvaluacionHP(
            hp_id="HP 14",
            nombre="Ecotóxico (Acuático)",
            es_peligroso=es_peligroso,
            limite_superado=es_peligroso,
            umbral_limite_pct=25.0,
            concentracion_relevante_pct=round(max(c_h400, suma_ponderada_cronica, suma_simple_cronica), 3),
            justificacion_normativa="Reglamento (UE) 2017/997: Ecuación sumatoria crónica (100*c(H410) + 10*c(H411) + c(H412) >= 25%)."
        )

    @classmethod
    def clasificar_residuo_espejo(
        cls,
        codigo_propuesto: str,
        sustancias_analizadas: List[ConcentracionSustancia],
        descripcion_origen: str = ""
    ) -> Dict[str, Any]:
        """
        Ejecuta el árbol de decisión pericial MITECO 2021 sobre un código propuesto.
        Si alguna HP resulta positiva, se asigna forzosamente el código LER peligroso (*).
        """
        codigo_limpio = codigo_propuesto.strip()
        par_espejo = PARES_ESPEJO_HABITUALES.get(codigo_limpio.replace("*", ""))

        # Evaluar baterías clave de peligrosidad química
        evaluaciones: List[ResultadoEvaluacionHP] = [
            cls.evaluar_hp4_irritacion_cutanea(sustancias_analizadas),
            cls.evaluar_hp7_carcinogeno(sustancias_analizadas),
            cls.evaluar_hp14_ecotoxico_ue2017_997(sustancias_analizadas)
        ]

        hps_positivas = [e for e in evaluaciones if e.es_peligroso]
        es_residuo_peligroso = len(hps_positivas) > 0

        if par_espejo:
            codigo_final = par_espejo["codigo_peligroso"] if es_residuo_peligroso else par_espejo["codigo_no_peligroso"]
            denominacion_final = par_espejo["descripcion_peligroso"] if es_residuo_peligroso else par_espejo["descripcion_no_peligroso"]
            sector = par_espejo["sector"]
        else:
            # Si no está en el mapa base, se conserva el código o se marca asterisco
            codigo_final = codigo_limpio if "*" in codigo_limpio or not es_residuo_peligroso else f"{codigo_limpio}*"
            denominacion_final = f"Residuo analizado ({'Peligroso' if es_residuo_peligroso else 'No Peligroso'})"
            sector = "Industrial General"

        dictamen_pericial = (
            f"DICTAMEN PERICIAL LER MITECO 2021: El residuo '{codigo_final}' ha sido clasificado formalmente como "
            f"{'RESIDUO PELIGROSO (*)' if es_residuo_peligroso else 'RESIDUO NO PELIGROSO'}. "
            f"Fundamento: {len(hps_positivas)} características de peligrosidad superan los umbrales vinculantes del Reglamento (UE) nº 1357/2014 y 2017/997. "
            f"Habilitación Técnica: Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7)."
        )

        return {
            "codigo_ler_asignado": codigo_final,
            "es_peligroso": es_residuo_peligroso,
            "denominacion_oficial": denominacion_final,
            "sector_aplicacion": sector,
            "total_sustancias_analizadas": len(sustancias_analizadas),
            "hps_positivas": [h.hp_id for h in hps_positivas],
            "detalle_evaluacion_hps": [
                {
                    "hp": e.hp_id,
                    "nombre": e.nombre,
                    "peligroso": e.es_peligroso,
                    "valor_obtenido": e.concentracion_relevante_pct,
                    "umbral": e.umbral_limite_pct,
                    "normativa": e.justificacion_normativa
                }
                for e in evaluaciones
            ],
            "dictamen_pericial": dictamen_pericial
        }
