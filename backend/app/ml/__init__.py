"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Machine learning module for anomaly detection and model training.
"""

from app.core.config import logger

# Import anomaly detection helpers
try:
    from app.ml.anomaly_detector import detect_anomaly, get_model_status  # type: ignore
except Exception as exc:  # pragma: no cover - optional dependency fallback
    logger.warning(f"Anomaly detector unavailable: {exc}. ML features disabled.")

    async def detect_anomaly(*args, **kwargs):  # type: ignore[override]
        logger.debug("detect_anomaly invoked but ML dependencies unavailable.")
        return False, 0.0

    def get_model_status() -> dict:  # type: ignore[override]
        return {
            "loaded": False,
            "tensorflow_available": False,
            "model_path": None,
            "model_exists": False,
            "threshold": 0.0,
        }

# Import training helpers
try:
    from app.ml.training import train_autoencoder_model, fetch_training_data  # type: ignore
except Exception as exc:  # pragma: no cover - optional dependency fallback
    logger.warning(f"Training module unavailable: {exc}. ML training disabled.")

    async def train_autoencoder_model(*args, **kwargs):  # type: ignore[override]
        logger.debug("train_autoencoder_model invoked but ML dependencies unavailable.")
        raise RuntimeError("ML training is disabled because required dependencies are missing.")

    async def fetch_training_data(*args, **kwargs):  # type: ignore[override]
        logger.debug("fetch_training_data invoked but ML dependencies unavailable.")
        return []

__all__ = [
    "detect_anomaly",
    "get_model_status",
    "train_autoencoder_model",
    "fetch_training_data",
]
