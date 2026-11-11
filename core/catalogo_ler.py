"""
CATÁLOGO EUROPEO DE RESIDUOS (LER) & MATRIZ DE HOMOLOGACIÓN NORMATIVA
Conforme a la Decisión 2014/955/UE, Reglamento (UE) nº 1357/2014 y Ley 7/2022 de Residuos.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ResiduoLER:
    codigo: str
    descripcion: str
    peligroso: bool
    caracteristica_hp: Optional[str]
    grupo_sanitario_espana: str
    tratamiento_normativo: str
    factor_emision_kgCO2e_kg: float
    tarifa_orientativa_eur_kg: float
    valorizable: bool


class CatalogoLER:
    """Motor y base de datos canónica del Catálogo Europeo de Residuos (LER)."""

    def __init__(self):
        self._database: Dict[str, ResiduoLER] = {
            "18 01 01": ResiduoLER(
                codigo="18 01 01",
                descripcion="Objetos cortantes y punzantes (agujas, lancetas, bisturís, ampollas de vidrio)",
                peligroso=True,
                caracteristica_hp="HP 9 (Infeccioso)",
                grupo_sanitario_espana="Grupo III (Biosanitarios Especiales)",
                tratamiento_normativo="Contenedor rígido imperforable (RRP) + Autoclave industrial o Incineración",
                factor_emision_kgCO2e_kg=1.800,
                tarifa_orientativa_eur_kg=1.30,
                valorizable=False
            ),
            "18 01 03*": ResiduoLER(
                codigo="18 01 03*",
                descripcion="Residuos cuya recogida y eliminación es objeto de requisitos especiales para prevenir infecciones (flujo biológico activo, cultivos)",
                peligroso=True,
                caracteristica_hp="HP 9 (Infeccioso)",
                grupo_sanitario_espana="Grupo III (Biosanitarios Especiales)",
                tratamiento_normativo="Esterilización por autoclave a vapor (descarbonizado) o Incineración térmica a 1.200 °C",
                factor_emision_kgCO2e_kg=1.800,
                tarifa_orientativa_eur_kg=1.30,
                valorizable=False
            ),
            "18 01 04": ResiduoLER(
                codigo="18 01 04",
                descripcion="Residuos cuya recogida y eliminación no es objeto de requisitos especiales para prevenir infecciones (gasas, apósitos limpios)",
                peligroso=False,
                caracteristica_hp=None,
                grupo_sanitario_espana="Grupo II (Biosanitarios Asimilables a Urbanos)",
                tratamiento_normativo="Vertedero controlado municipal o incineración con recuperación energética",
                factor_emision_kgCO2e_kg=0.580,
                tarifa_orientativa_eur_kg=0.15,
                valorizable=False
            ),
            "18 01 09": ResiduoLER(
                codigo="18 01 09",
                descripcion="Medicamentos distintos de los especificados en el código 18 01 08 (medicamentos caducados no citotóxicos ni citostáticos)",
                peligroso=False,
                caracteristica_hp=None,
                grupo_sanitario_espana="Grupo IV (Residuos Tipificados / Químicos)",
                tratamiento_normativo="Destrucción térmica en gestor autorizado / Sistema SIGRE hospitalario",
                factor_emision_kgCO2e_kg=1.100,
                tarifa_orientativa_eur_kg=1.30,
                valorizable=False
            ),
            "18 01 10*": ResiduoLER(
                codigo="18 01 10*",
                descripcion="Residuos de amalgama procedentes de cuidados dentales (presencia de mercurio metálico)",
                peligroso=True,
                caracteristica_hp="HP 14 (Ecotóxico) / HP 6 (Toxicidad aguda)",
                grupo_sanitario_espana="Grupo IV (Químicos y Metales Pesados)",
                tratamiento_normativo="Separador de amalgama con filtro + Recuperación fisicoquímica en planta autorizada",
                factor_emision_kgCO2e_kg=2.400,
                tarifa_orientativa_eur_kg=3.50,
                valorizable=True
            ),
            "20 03 01": ResiduoLER(
                codigo="20 03 01",
                descripcion="Mezcla de residuos domésticos / Fracción Resto (papel de aseo de pacientes, toallas de mano, barreduras)",
                peligroso=False,
                caracteristica_hp=None,
                grupo_sanitario_espana="Grupo I (Asimilables a Urbanos)",
                tratamiento_normativo="Recogida municipal hacia vertedero controlado o valorización energética",
                factor_emision_kgCO2e_kg=0.580,
                tarifa_orientativa_eur_kg=0.08,
                valorizable=False
            ),
            "15 01 01": ResiduoLER(
                codigo="15 01 01",
                descripcion="Envases de papel y cartón procedentes de farmacia, almacén y logística",
                peligroso=False,
                caracteristica_hp=None,
                grupo_sanitario_espana="Grupo I (Valorizables)",
                tratamiento_normativo="Segregación en origen y reciclaje mecánico en papelera (Economía Circular)",
                factor_emision_kgCO2e_kg=-0.700,
                tarifa_orientativa_eur_kg=-0.05,
                valorizable=True
            ),
            "15 01 02": ResiduoLER(
                codigo="15 01 02",
                descripcion="Envases de plástico film, botellas de polietileno y envases secundarios no contaminados",
                peligroso=False,
                caracteristica_hp=None,
                grupo_sanitario_espana="Grupo I (Valorizables)",
                tratamiento_normativo="Recogida selectiva y reciclaje mecánico (evitación de polímero virgen)",
                factor_emision_kgCO2e_kg=-0.700,
                tarifa_orientativa_eur_kg=-0.04,
                valorizable=True
            ),
            "17 01 01": ResiduoLER(
                codigo="17 01 01",
                descripcion="Hormigón de demolición y cimentaciones de obra civil",
                peligroso=False,
                caracteristica_hp=None,
                grupo_sanitario_espana="RCD Inerte (No sanitario)",
                tratamiento_normativo="Planta de machaqueo para producción de árido reciclado (RD 105/2008)",
                factor_emision_kgCO2e_kg=0.012,
                tarifa_orientativa_eur_kg=0.02,
                valorizable=True
            ),
            "17 09 04": ResiduoLER(
                codigo="17 09 04",
                descripcion="Residuos mezclados de construcción y demolición distintos de los especificados en los códigos 17 09 01, 17 09 02 y 17 09 03",
                peligroso=False,
                caracteristica_hp=None,
                grupo_sanitario_espana="RCD Fracción Resto",
                tratamiento_normativo="Clasificación en planta RCD y vertido de rechazo (Impuesto Ley 7/2022: 40 €/t)",
                factor_emision_kgCO2e_kg=0.045,
                tarifa_orientativa_eur_kg=0.05,
                valorizable=False
            )
        }

    def obtener_residuo(self, codigo: str) -> Optional[ResiduoLER]:
        """Obtiene la ficha técnica de un código LER normalizado."""
        codigo_limpio = codigo.strip().replace("*", "").strip()
        # Búsqueda exacta
        for k, v in self._database.items():
            if k.replace("*", "").strip() == codigo_limpio:
                return v
        return None

    def listar_todos(self) -> List[ResiduoLER]:
        """Retorna la lista completa de códigos registrados."""
        return list(self._database.values())

    def buscar_por_termino(self, termino: str) -> List[ResiduoLER]:
        """Busca códigos LER que coincidan por código o descripción."""
        termino_lower = termino.lower()
        return [
            r for r in self._database.values()
            if termino_lower in r.codigo.lower() or termino_lower in r.descripcion.lower()
        ]

    @property
    def catalogo(self) -> Dict[str, ResiduoLER]:
        """Acceso directo a la base de datos de residuos LER."""
        return self._database

    def es_peligroso(self, codigo: str) -> bool:
        """Determina de forma determinista si un código LER es peligroso."""
        res = self.obtener_residuo(codigo)
        if res:
            return res.peligroso
        return "*" in codigo
