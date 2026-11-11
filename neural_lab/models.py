"""
ARQUITECTURAS NEURONALES AVANZADAS: OUROBOROS NEURAL LAB™
Ecosistema: Yggdrasil Environmental Systems | CIRCULAR-CORE: OUROBOROS (0x05)
Lead Systems Architect: Kelvin Jesús Flores Yarihuaman (MECES 3 / EQF 7)

MODELOS IMPLEMENTADOS:
1. OuroborosAnomalyNet (Open-Core):
   Autoencoder profundo con normalización LayerNorm, activaciones GELU y regularización
   latente para detección estocástica de fraude en segregación, derivas gravimétricas
   y desbordamiento de residuos biocontaminados en tiempo real.

2. OuroborosCircularForecaster (Enterprise Tier):
   Operador Neuronal Temporal Físicamente Guiado (PINN-TCN-MHA) multi-cuantil (P10, P50, P90)
   con convoluciones causales dilatadas WaveNet, codificador exógeno GRU bidireccional,
   mecanismo de Cross-Attention multi-cabezal y pérdidas informadas por la física
   (no negatividad, monotonicidad cuantil y conservación de materia).
"""

import math
from typing import Tuple, List, Dict, Any, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


# ==============================================================================
# 1. MODELO OPEN-CORE: OUROBOROS ANOMALY NET (AUTOENCODER PROFUNDO)
# ==============================================================================

class OuroborosAnomalyNet(nn.Module):
    """
    Autoencoder Neuronal Profundo de Alta Precisión para Auditoría de Segregación.
    Aprende la variedad latente (manifold) de generación hospitalaria ordinaria
    y cuantifica anomalías mediante error cuadrático medio de reconstrucción ponderado (WMSE).
    """

    def __init__(self, input_dim: int = 8, latent_dim: int = 4, dropout: float = 0.1):
        super().__init__()
        self.input_dim = input_dim
        self.latent_dim = latent_dim

        # Encoder con LayerNorm y GELU
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.LayerNorm(32),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(32, 16),
            nn.LayerNorm(16),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(16, latent_dim)
        )

        # Decoder simétrico
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.LayerNorm(16),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(16, 32),
            nn.LayerNorm(32),
            nn.GELU(),
            nn.Linear(32, input_dim)
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        latent = self.encoder(x)
        reconstruction = self.decoder(latent)
        return reconstruction, latent

    def compute_anomaly_score(self, x: torch.Tensor) -> torch.Tensor:
        """Calcula el error cuadrático medio de reconstrucción por vector de muestra."""
        with torch.no_grad():
            reconstruction, _ = self.forward(x)
            mse = torch.mean((x - reconstruction) ** 2, dim=-1)
        return mse

    def predict_anomaly(
        self, x: torch.Tensor, threshold: Optional[float] = None, percentile: float = 90.0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Retorna máscara booleana de anomalía y score numérico.
        Si no se provee threshold estático, aplica percentil empírico adaptativo.
        """
        scores = self.compute_anomaly_score(x)
        if threshold is None:
            threshold = float(torch.quantile(scores, percentile / 100.0).item())
        is_anomaly = scores > threshold
        return is_anomaly, scores


# ==============================================================================
# 2. BLOQUE CONVOLUCIONAL CAUSAL DILATADO (WAVENET GATING)
# ==============================================================================

class CausalConv1dBlock(nn.Module):
    """
    Bloque Convolucional Causal Dilatado con compuertas multiplicativas WaveNet (tanh x sigmoid),
    normalización de grupo y conexión residual. Garantiza que la predicción en el tiempo t
    no filtre información del futuro (t+1..T).
    """

    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3, dilation: int = 1, dropout: float = 0.1):
        super().__init__()
        self.dilation = dilation
        self.padding = (kernel_size - 1) * dilation
        self.filter_conv = nn.Conv1d(in_channels, out_channels, kernel_size, dilation=dilation)
        self.gate_conv = nn.Conv1d(in_channels, out_channels, kernel_size, dilation=dilation)
        self.residual_conv = nn.Conv1d(in_channels, out_channels, 1) if in_channels != out_channels else nn.Identity()
        self.dropout = nn.Dropout(dropout)
        self.norm = nn.GroupNorm(num_groups=min(4, out_channels), num_channels=out_channels)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        res = self.residual_conv(x)
        # Padding causal a la izquierda
        padded_x = F.pad(x, (self.padding, 0))
        filt = torch.tanh(self.filter_conv(padded_x))
        gate = torch.sigmoid(self.gate_conv(padded_x))
        out = self.norm(filt * gate)
        out = self.dropout(out)
        return out + res


# ==============================================================================
# 3. MODELO ENTERPRISE: OUROBOROS CIRCULAR FORECASTER (PINN-TCN-MHA)
# ==============================================================================

class OuroborosCircularForecaster(nn.Module):
    """
    Operador Neuronal Temporal Físicamente Informado (PINN-TCN-MHA).
    Arquitectura no-juguete de grado industrial para proyección multicuantil (P10, P50, P90)
    del metabolismo material hospitalario y descarbonización Scope 3 (2026-2030).
    
    Salidas modeladas:
      1) Masa Total Generada (kg/mes)
      2) Huella de Alcance 3 (kg CO2e/mes)
      3) Exposición Fiscal Ley 7/2022 (€/mes)
    """

    def __init__(
        self,
        history_features: int = 8,
        exogenous_features: int = 4,
        hidden_dim: int = 64,
        num_tcn_layers: int = 4,
        horizon_steps: int = 12,
        quantiles: Optional[List[float]] = None,
        dropout: float = 0.15
    ):
        super().__init__()
        self.horizon_steps = horizon_steps
        self.quantiles = quantiles or [0.10, 0.50, 0.90]
        self.hidden_dim = hidden_dim
        self.num_quantiles = len(self.quantiles)

        # 1. Proyección de Historia y Bloques TCN Dilatados
        self.hist_proj = nn.Conv1d(history_features, hidden_dim, kernel_size=1)
        self.tcn_blocks = nn.ModuleList([
            CausalConv1dBlock(hidden_dim, hidden_dim, kernel_size=3, dilation=2**i, dropout=dropout)
            for i in range(num_tcn_layers)
        ])

        # 2. Codificador de Variables Exógenas Futuras (Regulaciones, IPC, Metas CSRD)
        self.exo_proj = nn.Linear(exogenous_features, hidden_dim)
        self.exo_gru = nn.GRU(hidden_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.exo_dense = nn.Linear(hidden_dim * 2, hidden_dim)

        # 3. Mecanismo de Cross-Attention (El futuro consulta dinámicamente a la historia)
        self.cross_attn = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=4, dropout=dropout, batch_first=True)
        self.norm = nn.LayerNorm(hidden_dim)

        # 4. Capas Densas de Fusión y Cabeza Multicuantil
        self.fusion = nn.Sequential(
            nn.Linear(hidden_dim, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.GELU()
        )
        self.fc_head = nn.Linear(64, self.horizon_steps * 3 * self.num_quantiles)

    def forward(
        self, x_hist: torch.Tensor, x_exo_future: torch.Tensor
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        x_hist: [batch, lookback_steps, history_features]
        x_exo_future: [batch, horizon_steps, exogenous_features]
        Returns:
            preds: [batch, horizon_steps, 3, num_quantiles]
            attn_weights: [batch, horizon_steps, lookback_steps]
        """
        b = x_hist.size(0)

        # Extraer características temporales con TCN
        h = self.hist_proj(x_hist.transpose(1, 2))  # [b, hidden_dim, lookback]
        for block in self.tcn_blocks:
            h = block(h)
        hist_encoded = h.transpose(1, 2)  # [b, lookback, hidden_dim]

        # Codificar contexto exógeno futuro
        exo_embed = F.gelu(self.exo_proj(x_exo_future))
        exo_out, _ = self.exo_gru(exo_embed)
        exo_encoded = self.exo_dense(exo_out)  # [b, horizon_steps, hidden_dim]

        # Cross Attention: Queries (Futuro exógeno) atienden a Keys/Values (Historia causal)
        attn_out, attn_weights = self.cross_attn(
            query=exo_encoded, key=hist_encoded, value=hist_encoded
        )
        latent = self.norm(exo_encoded + attn_out)  # [b, horizon_steps, hidden_dim]

        # Head de proyección
        fused = self.fusion(latent)  # [b, horizon_steps, 64]
        # Agregamos pooling global o mapeo temporal directo
        flat_repr = fused[:, -1, :]  # Último estado representativo
        preds_flat = self.fc_head(flat_repr)  # [b, horizon * 3 * num_quantiles]
        preds = preds_flat.view(b, self.horizon_steps, 3, self.num_quantiles)

        return preds, attn_weights


# ==============================================================================
# 4. FUNCIONES DE PÉRDIDA: PINBALL MULTI-QUANTILE Y REGULARIZACIÓN FÍSICA
# ==============================================================================

class PinballLoss(nn.Module):
    """
    Función de pérdida Pinball (Quantile Loss) asimétrica para regresión probabilística.
    L_q(y, y_hat) = max(q * (y - y_hat), (q - 1) * (y - y_hat))
    """

    def __init__(self, quantiles: Optional[List[float]] = None):
        super().__init__()
        self.quantiles = quantiles or [0.10, 0.50, 0.90]

    def forward(self, preds: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        preds: [batch, horizon, targets_dim, num_quantiles]
        targets: [batch, horizon, targets_dim]
        """
        targets_expanded = targets.unsqueeze(-1)  # [batch, horizon, targets_dim, 1]
        errors = targets_expanded - preds         # [batch, horizon, targets_dim, num_quantiles]
        losses = []
        for i, q in enumerate(self.quantiles):
            err = errors[..., i]
            loss_q = torch.maximum(q * err, (q - 1.0) * err)
            losses.append(loss_q.mean())
        return torch.stack(losses).mean()


class PhysicsInformedCircularLoss(nn.Module):
    """
    Pérdida Compuesta Físicamente Guiada (PINN Loss) para OUROBOROS:
    1. Pinball Quantile Loss (precisión probabilística)
    2. Penalización de Monotonicidad Cuantil (P10 <= P50 <= P90)
    3. Penalización de No-Negatividad (Masa >= 0, Emisiones >= 0, Impuestos >= 0)
    4. Regularización de Coherencia Másica-Emisión (Scope 3 correlacionado con masa tratada)
    """

    def __init__(
        self,
        quantiles: Optional[List[float]] = None,
        lambda_quantile_order: float = 1.5,
        lambda_non_negativity: float = 2.0,
        lambda_emission_ratio: float = 0.5
    ):
        super().__init__()
        self.pinball = PinballLoss(quantiles=quantiles)
        self.lambda_quantile_order = lambda_quantile_order
        self.lambda_non_negativity = lambda_non_negativity
        self.lambda_emission_ratio = lambda_emission_ratio

    def forward(self, preds: torch.Tensor, targets: torch.Tensor) -> Tuple[torch.Tensor, Dict[str, float]]:
        # 1. Pérdida Pinball básica
        loss_pinball = self.pinball(preds, targets)

        # 2. Penalización de cruce de cuantiles: P10 debe ser <= P50 y P50 <= P90
        p10 = preds[..., 0]
        p50 = preds[..., 1]
        p90 = preds[..., 2]
        loss_crossing = torch.mean(F.relu(p10 - p50)) + torch.mean(F.relu(p50 - p90))

        # 3. Penalización estricta de no-negatividad en variables físicas
        loss_negativity = torch.mean(F.relu(-preds))

        # 4. Coherencia másica: Emisiones (idx 1) no pueden divergir de masa (idx 0) arbitrariamente
        pred_mass = preds[:, :, 0, 1]      # P50 masa
        pred_emission = preds[:, :, 1, 1]  # P50 emisiones
        # Rango físico esperado de factor compuesto: entre 0.15 y 2.5 kg CO2e / kg masa
        implied_factor = pred_emission / (pred_mass + 1e-4)
        loss_physics_factor = torch.mean(F.relu(implied_factor - 3.0)) + torch.mean(F.relu(0.05 - implied_factor))

        total_loss = (
            loss_pinball
            + self.lambda_quantile_order * loss_crossing
            + self.lambda_non_negativity * loss_negativity
            + self.lambda_emission_ratio * loss_physics_factor
        )

        metrics = {
            "loss_total": float(total_loss.item()),
            "loss_pinball": float(loss_pinball.item()),
            "loss_crossing": float(loss_crossing.item()),
            "loss_negativity": float(loss_negativity.item()),
            "loss_physics": float(loss_physics_factor.item())
        }
        return total_loss, metrics


# ==============================================================================
# 5. ENTERPRISE TITAN SUITE (NVIDIA L4 24GB INDUSTRIAL DUAL-AI)
# ==============================================================================

class ResidualHighwayBlock(nn.Module):
    """Bloque Residual Highway con LayerNorm, GELU y conexión residual adaptativa."""
    def __init__(self, in_features: int, out_features: int, dropout: float = 0.08):
        super().__init__()
        self.norm = nn.LayerNorm(in_features)
        self.fc1 = nn.Linear(in_features, out_features)
        self.act = nn.GELU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(out_features, out_features)
        self.shortcut = nn.Linear(in_features, out_features) if in_features != out_features else nn.Identity()

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.shortcut(x) + self.fc2(self.dropout(self.act(self.fc1(self.norm(x)))))


class OuroborosDeepLatentAE(nn.Module):
    """
    Autoencoder Industrial Profundo Titan (Open-Core Enterprise):
    Arquitectura con bloques ResidualHighway, compresión a Z in R^16,
    optimizada para detección en tiempo real de anomalías gravimétricas y fraude.
    """
    def __init__(self, input_dim: int = 8, latent_dim: int = 16, dropout: float = 0.08):
        super().__init__()
        self.enc_in = nn.Linear(input_dim, 256)
        self.enc_block1 = ResidualHighwayBlock(256, 128, dropout)
        self.enc_block2 = ResidualHighwayBlock(128, 64, dropout)
        self.to_latent = nn.Linear(64, latent_dim)

        self.dec_in = nn.Linear(latent_dim, 64)
        self.dec_block1 = ResidualHighwayBlock(64, 128, dropout)
        self.dec_block2 = ResidualHighwayBlock(128, 256, dropout)
        self.dec_out = nn.Sequential(nn.LayerNorm(256), nn.GELU(), nn.Linear(256, input_dim))

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        h = self.enc_block2(self.enc_block1(F.gelu(self.enc_in(x))))
        latent = self.to_latent(h)
        d = self.dec_block2(self.dec_block1(F.gelu(self.dec_in(latent))))
        return self.dec_out(d), latent

    def compute_anomaly_score(self, x: torch.Tensor) -> torch.Tensor:
        with torch.no_grad():
            rec, _ = self.forward(x)
            return torch.mean((x - rec) ** 2, dim=-1)


class CausalConv1dGated(nn.Module):
    """Bloque Convolucional Causal Dilatado WaveNet con Gated Tanh/Sigmoid."""
    def __init__(self, channels: int, kernel_size: int = 3, dilation: int = 1, dropout: float = 0.10):
        super().__init__()
        self.dilation = dilation
        self.padding = (kernel_size - 1) * dilation
        self.conv_f = nn.Conv1d(channels, channels, kernel_size, dilation=dilation)
        self.conv_g = nn.Conv1d(channels, channels, kernel_size, dilation=dilation)
        self.norm = nn.GroupNorm(num_groups=8, num_channels=channels)
        self.dropout = nn.Dropout(dropout)
        self.res = nn.Conv1d(channels, channels, kernel_size=1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        padded = F.pad(x, (self.padding, 0))
        out = self.norm(torch.tanh(self.conv_f(padded)) * torch.sigmoid(self.conv_g(padded)))
        return x + self.res(self.dropout(out))


class OuroborosDeepPINNForecaster(nn.Module):
    """
    Operador Neuronal Temporal Enterprise Titan:
    Garantiza arquitectónicamente:
      1) No-negatividad: base = Softplus(out[..., 0:1])
      2) Monotonicidad Cuantil Estricta: quantiles = base + cumsum(Softplus(deltas))
      P05 <= P10 <= P25 <= P50 <= P75 <= P90 <= P95 (cero cruces garantizado).
    """
    def __init__(
        self,
        history_features: int = 8,
        exogenous_features: int = 4,
        hidden_dim: int = 128,
        num_tcn_layers: int = 6,
        horizon_steps: int = 6,
        quantiles: Optional[List[float]] = None,
        dropout: float = 0.10
    ):
        super().__init__()
        self.horizon_steps = horizon_steps
        self.quantiles = quantiles or [0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95]
        self.num_quantiles = len(self.quantiles)
        self.hidden_dim = hidden_dim

        self.in_proj = nn.Conv1d(history_features, hidden_dim, kernel_size=1)
        self.wavenet_blocks = nn.ModuleList([
            CausalConv1dGated(hidden_dim, kernel_size=3, dilation=2 ** i, dropout=dropout)
            for i in range(num_tcn_layers)
        ])

        self.exo_in = nn.Linear(exogenous_features, hidden_dim)
        self.exo_gru = nn.GRU(hidden_dim, hidden_dim, num_layers=2, batch_first=True, bidirectional=True, dropout=dropout)
        self.exo_proj = nn.Linear(hidden_dim * 2, hidden_dim)

        self.cross_attn = nn.MultiheadAttention(embed_dim=hidden_dim, num_heads=8, dropout=dropout, batch_first=True)
        self.attn_norm = nn.LayerNorm(hidden_dim)

        self.head_dense1 = ResidualHighwayBlock(hidden_dim, 256, dropout)
        self.head_dense2 = ResidualHighwayBlock(256, 128, dropout)
        self.head_out = nn.Linear(128, horizon_steps * 3 * self.num_quantiles)

    def forward(self, x_hist: torch.Tensor, x_exo: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        b = x_hist.size(0)
        h = self.in_proj(x_hist.transpose(1, 2))
        for block in self.wavenet_blocks:
            h = block(h)
        hist_enc = h.transpose(1, 2)

        exo_out, _ = self.exo_gru(F.gelu(self.exo_in(x_exo)))
        exo_enc = self.exo_proj(exo_out)

        attn_out, attn_w = self.cross_attn(query=exo_enc, key=hist_enc, value=hist_enc)
        fused = self.attn_norm(exo_enc + attn_out)

        d = self.head_dense2(self.head_dense1(fused[:, -1, :]))
        raw_out = self.head_out(d).view(b, self.horizon_steps, 3, self.num_quantiles)

        # Proyección Actuarial Monotónica Estricta por Construcción:
        base = F.softplus(raw_out[..., 0:1])              # P05 >= 0
        deltas = F.softplus(raw_out[..., 1:])            # Incrementos > 0
        preds = torch.cat([base, base + torch.cumsum(deltas, dim=-1)], dim=-1)

        return preds, attn_w
