"""
CIRCULAR-CORE: OUROBOROS (0x05)
Yggdrasil Environmental Systems - Core Engine de Metabolismo Material y Descarbonización Integral
"""

from .catalogo_ler import CatalogoLER, ResiduoLER
from .gravimetria import MotorGravimetrico
from .scope1_direct_engine import MotorScope1
from .scope2_electricity_engine import MotorScope2
from .scope3_waste_engine import MotorScope3
from .acv_iso14040 import MotorACV

__all__ = [
    "CatalogoLER",
    "ResiduoLER",
    "MotorGravimetrico",
    "MotorScope1",
    "MotorScope2",
    "MotorScope3",
    "MotorACV"
]
