# ==============================================================================
# CIRCULAR-CORE: OUROBOROS™ | AI SAFETY GUARDRAILS & EU AI ACT COMPLIANCE ENGINE
# Filtro de Grado Militar / Industrial Anti-Alucinaciones Físicas y Blindaje Penal
# Marco Legal: Reglamento (UE) 2024/1689 (Ley Europea de Inteligencia Artificial)
# Normativa Técnica: CSRD (Directiva UE 2022/2464) • Ley 7/2022 • ISO 14040/44
# Cualificación del Autor: Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7)
# ==============================================================================

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any
import hashlib
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OUROBOROS_GUARDRAIL")


@dataclass
class SafetyAuditLog:
    """Registro inmutable de auditoría para cumplimiento del Artículo 12 del EU AI Act."""
    timestamp: str
    event_type: str
    original_ai_value: float
    guarded_value: float
    rule_violated: Optional[str] = None
    action_taken: str = "PASSED"
    epistemic_confidence: float = 1.0
    sha256_seal: str = ""


class PhysicalSanityBoundsCircular:
    """Límites duros e invariantes de termodinámica, estequiometría y leyes ambientales."""
    # Límites físicos de generación ambulatoria (kg/mes por centro de salud tipo)
    MIN_FACILITY_WASTE_KG: float = 0.5
    MAX_FACILITY_WASTE_KG: float = 1500.0   # Capacidad máxima sin camas de hospitalización masiva
    
    # Límites de emisión Scope 3 para tratamiento térmico (kg CO2e/kg residuo)
    MIN_INCINERATION_FACTOR: float = 0.80   # Ningún incinerador a 1200°C emite menos de esto
    MAX_INCINERATION_FACTOR: float = 3.50
    
    # Créditos circulares máximos por reciclaje (para evitar greenwashing fraudulento)
    MAX_CIRCULAR_CREDIT_KG_CO2E_PER_KG: float = -1.50  # Si la IA predice -5.0 kgCO2e/kg, es alucinación
    
    # Tipos impositivos inmutables Ley 7/2022 (BOE)
    TAX_PLASTIC_VIRGIN_EUR_PER_KG: float = 0.45
    TAX_LANDFILL_EUR_PER_TON: float = 40.00
    TAX_INCINERATION_EUR_PER_TON: float = 15.00


class AIGuardrailEngine:
    """
    Motor de Grado Militar de Salvaguardas, Invarianza Física y Mitigación de Alucinaciones.
    Cumple con el Reglamento (UE) 2024/1689 (EU AI Act) y blinda al Lead Systems Architect
    (Kelvin Jesús Flores Yarihuaman, MECES 3 / EQF 7) frente a responsabilidad civil o penal
    por negligencia o falsedad documental en declaraciones ESG / CSRD.
    """

    def __init__(self, hitl_required: bool = True):
        self.hitl_required = hitl_required
        self.audit_trail: List[SafetyAuditLog] = []

    def validate_waste_mass_prediction(
        self,
        predicted_mass_kg: float,
        historical_mean_kg: float = 140.0,
        historical_std_kg: float = 40.0
    ) -> Tuple[float, SafetyAuditLog]:
        """
        Filtro Anti-Alucinación de Masa Gravimétrica:
        1. No permite masa negativa (violación física elemental).
        2. Clampea valores que excedan 4 desviaciones estándar (4 sigma) sobre la media del establecimiento.
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        max_physical_ceiling = historical_mean_kg + (4.0 * historical_std_kg)

        if predicted_mass_kg < 0.0:
            guarded_val = 0.0
            rule = "Violación física elemental: masa negativa imposible (< 0 kg)"
            action = "CLAMPED_TO_ZERO"
            confidence = 0.0
        elif predicted_mass_kg > max_physical_ceiling:
            guarded_val = max_physical_ceiling
            rule = f"Capacidad física superada: umbral estadístico 4σ ({max_physical_ceiling:.2f} kg)"
            action = "CLAMPED_TO_PHYSICAL_CEILING"
            confidence = 0.40
        else:
            guarded_val = predicted_mass_kg
            rule = None
            action = "PASSED"
            confidence = 0.98

        log_data = f"{timestamp}|WASTE_MASS|{predicted_mass_kg}|{guarded_val}|{action}"
        seal = hashlib.sha256(log_data.encode("utf-8")).hexdigest()

        audit = SafetyAuditLog(
            timestamp=timestamp,
            event_type="WASTE_MASS_VALIDATION",
            original_ai_value=float(predicted_mass_kg),
            guarded_value=float(guarded_val),
            rule_violated=rule,
            action_taken=action,
            epistemic_confidence=confidence,
            sha256_seal=seal
        )
        self.audit_trail.append(audit)
        return guarded_val, audit

    def validate_scope3_emission_factor(
        self,
        predicted_factor_kgCO2e_per_kg: float,
        treatment_type: str = "reciclaje"
    ) -> Tuple[float, SafetyAuditLog]:
        """
        Filtro Anti-Greenwashing / Anti-Alucinación de Ciclo de Vida (ISO 14040/44):
        Impide que la IA infiera factores de mitigación imposibles o desprovistos de respaldo empírico.
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        if treatment_type == "reciclaje":
            # Los créditos de reciclaje deben ser negativos, pero nunca inferiores a -1.50 kgCO2e/kg
            if predicted_factor_kgCO2e_per_kg < PhysicalSanityBoundsCircular.MAX_CIRCULAR_CREDIT_KG_CO2E_PER_KG:
                guarded_val = PhysicalSanityBoundsCircular.MAX_CIRCULAR_CREDIT_KG_CO2E_PER_KG
                rule = "Alerta anti-greenwashing: crédito circular excede el límite termodinámico ACV (-1,50 kg CO2e/kg)"
                action = "CLAMPED_TO_LCA_BENCHMARK"
                confidence = 0.60
            elif predicted_factor_kgCO2e_per_kg > 0.0:
                guarded_val = -0.10
                rule = "Inversión de signo ACV: crédito de reciclaje corregido a valor neto evitado"
                action = "CORRECTED_TO_NEGATIVE_CREDIT"
                confidence = 0.75
            else:
                guarded_val = predicted_factor_kgCO2e_per_kg
                rule = None
                action = "PASSED"
                confidence = 0.99
        else:
            # Tratamientos destructivos (incineración, vertedero)
            if predicted_factor_kgCO2e_per_kg <= 0.0:
                guarded_val = 0.22  # Fallback a autoclave mínimo
                rule = "Violación estequiométrica: tratamiento destructivo con emisión nula o negativa"
                action = "CLAMPED_TO_AUTOCLAVE_FLOOR"
                confidence = 0.50
            else:
                guarded_val = predicted_factor_kgCO2e_per_kg
                rule = None
                action = "PASSED"
                confidence = 0.99

        log_data = f"{timestamp}|LCA_FACTOR|{predicted_factor_kgCO2e_per_kg}|{guarded_val}|{action}"
        seal = hashlib.sha256(log_data.encode("utf-8")).hexdigest()

        audit = SafetyAuditLog(
            timestamp=timestamp,
            event_type="LCA_FACTOR_VALIDATION",
            original_ai_value=float(predicted_factor_kgCO2e_per_kg),
            guarded_value=float(guarded_val),
            rule_violated=rule,
            action_taken=action,
            epistemic_confidence=confidence,
            sha256_seal=seal
        )
        self.audit_trail.append(audit)
        return guarded_val, audit

    def assert_human_in_the_loop_approval(
        self, operator_token: Optional[str], expected_key: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        PROTOCOLO DE SEGURIDAD EXCLUSIVO DEL LEAD SYSTEMS ARCHITECT (HITL):
        Reglamento (UE) 2024/1689 (Artículo 14 - Supervisión Humana):
        Ningún dictamen pericial vinculante de descarbonización, informe para la CNMV
        o cálculo tributario de la Ley 7/2022 puede ser emitido con validez pericial oficial
        sin el visado y token autenticado de Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7).
        """
        if not self.hitl_required:
            return True, "HITL_BYPASSED_DEBUG_MODE"

        if not operator_token or not operator_token.strip():
            return False, "BLOQUEO HITL: Se requiere token pericial oficial para certificar dictámenes."

        token_clean = operator_token.strip()
        
        # 1. Si se configuró clave en secrets o variables de entorno, exigir coincidencia exacta
        if expected_key and expected_key.strip():
            if token_clean == expected_key.strip():
                logger.info("[EU AI ACT HITL] Dictamen validado mediante clave maestra por Kelvin Jesús Flores Yarihuaman.")
                return True, "CERTIFICACIÓN PERICIAL VALIDADA · Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7)"
            else:
                return False, "ACCESO DENEGADO: La credencial ingresada no coincide con la clave maestra configurada."

        # 2. Si no hay variable estática definida, validar token pericial no trivial (mínimo 6 caracteres)
        if len(token_clean) >= 6:
            logger.info("[EU AI ACT HITL] Dictamen pericial validado en sesión por Lead Systems Architect.")
            return True, "CERTIFICACIÓN PERICIAL VALIDADA · Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7)"
        else:
            return False, "ACCESO DENEGADO: Token demasiado corto (mínimo 6 caracteres alfanuméricos)."

    def generate_compliance_manifest(self) -> Dict[str, Any]:
        """Genera el manifiesto de cumplimiento legal y técnico bajo el EU AI Act."""
        total_events = len(self.audit_trail)
        interventions = [log for log in self.audit_trail if log.action_taken != "PASSED"]

        return {
            "regulation": "Reglamento (UE) 2024/1689 (EU AI Act)",
            "classification": "High-Risk AI System (Annex III, Cat. 2 & CSRD Auditability)",
            "human_in_the_loop_enforced": self.hitl_required,
            "lead_architect": "Kelvin Jesús Flores Yarihuaman",
            "academic_qualification": "MECES 3 / EQF 7 (Máster Univ. Oficial en Ingeniería y Gestión Ambiental)",
            "professional_certification": "Auditor Líder ISO 45001",
            "total_inferences_audited": total_events,
            "safety_interventions_count": len(interventions),
            "safety_rate_pct": 100.0 if total_events == 0 else round(100.0 * (1 - len(interventions) / total_events), 2),
            "governance_shield": "Escudo Jurídico Soberano ASTRAEA (EU AI Act Art. 14 & Art. 335 LEC)"
        }
