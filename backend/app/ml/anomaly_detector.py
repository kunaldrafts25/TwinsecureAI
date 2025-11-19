"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

ML-based anomaly detection using TensorFlow/Keras autoencoder.
"""

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, Any

from app.core.config import logger, settings

# Optional dependencies for ML features
ML_DEPENDENCIES_AVAILABLE = True

try:
    import numpy as np
except ImportError:
    ML_DEPENDENCIES_AVAILABLE = False
    np = None  # type: ignore[assignment]
    logger.warning("NumPy not available. ML anomaly detection disabled.")

try:
    import pandas as pd
except ImportError:
    ML_DEPENDENCIES_AVAILABLE = False
    pd = None  # type: ignore[assignment]
    logger.warning("Pandas not available. ML anomaly detection disabled.")

try:
    from sklearn.preprocessing import StandardScaler
except ImportError:
    ML_DEPENDENCIES_AVAILABLE = False
    StandardScaler = None  # type: ignore[assignment]
    logger.warning("scikit-learn not available. ML anomaly detection disabled.")

# Try to import TensorFlow, handle gracefully if not available
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False
    keras = None  # Set to None for type hints
    logger.warning("TensorFlow not available. ML anomaly detection disabled.")

# Type hint for model (use Any if TensorFlow not available)
if TYPE_CHECKING:
    if TENSORFLOW_AVAILABLE:
        ModelType = keras.Model
    else:
        ModelType = Any
    from sklearn.preprocessing import StandardScaler as SklearnStandardScaler  # pragma: no cover
else:
    ModelType = Any
    SklearnStandardScaler = Any  # type: ignore[misc]

# Global model state
_model: ModelType | None = None
_scaler: SklearnStandardScaler | None = None
_anomaly_threshold: float = 0.05
_model_loaded: bool = False

# Feature columns expected by the model
FEATURE_COLUMNS = [
    "request_freq",
    "url_entropy",
    "response_time",
    "payload_size",
    "status_code_ratio",
    "unique_ips",
    "connection_duration",
    "bytes_sent",
    "bytes_received",
    "protocol_type",
]


def _load_model() -> bool:
    """Load the trained model and scaler from disk."""
    global _model, _scaler, _anomaly_threshold, _model_loaded
    
    if not TENSORFLOW_AVAILABLE or not ML_DEPENDENCIES_AVAILABLE:
        return False
    
    if _model_loaded:
        return True
    
    if not settings.ML_MODEL_PATH:
        logger.warning("ML_MODEL_PATH not configured. Anomaly detection disabled.")
        return False
    
    model_path = Path(settings.ML_MODEL_PATH)
    if not model_path.exists():
        logger.warning(f"ML model not found at {model_path}. Anomaly detection disabled.")
        return False
    
    try:
        # Load the model
        _model = keras.models.load_model(str(model_path))
        logger.info(f"ML anomaly detection model loaded from {model_path}")
        
        # Load scaler (saved alongside the model)
        scaler_path = model_path.parent / "scaler.pkl"
        if scaler_path.exists():
            import joblib
            _scaler = joblib.load(scaler_path)
            logger.info(f"Scaler loaded from {scaler_path}")
        else:
            logger.warning("Scaler not found, creating new one. Model may not work correctly.")
            _scaler = StandardScaler()
        
        # Load threshold (if saved)
        threshold_path = model_path.parent / "threshold.txt"
        if threshold_path.exists():
            with open(threshold_path) as f:
                _anomaly_threshold = float(f.read().strip())
            logger.info(f"Anomaly threshold loaded: {_anomaly_threshold}")
        
        _model_loaded = True
        return True
        
    except Exception as e:
        logger.error(f"Failed to load ML model: {e}", exc_info=True)
        _model = None
        _scaler = None
        return False


async def detect_anomaly(traffic_vector: dict) -> tuple[bool, float]:
    """
    Analyze traffic vector using trained autoencoder to detect anomalies.
    
    Args:
        traffic_vector: Dictionary of traffic features
            (e.g., {'request_freq': 10, 'url_entropy': 2.5, ...})
    
    Returns:
        Tuple of (is_anomaly, reconstruction_error)
        is_anomaly is True if error exceeds threshold
    """
    global _model, _scaler, _anomaly_threshold
    
    # Load model if not already loaded
    if not _model_loaded:
        loop = asyncio.get_running_loop()
        loaded = await loop.run_in_executor(None, _load_model)
        if not loaded:
            logger.debug("ML model not available. Skipping anomaly detection.")
            return False, 0.0
    
    if not _model or not _scaler or not ML_DEPENDENCIES_AVAILABLE or np is None or pd is None:
        logger.debug("ML model or scaler not loaded. Skipping anomaly detection.")
        return False, 0.0
    
    try:
        # 1. Preprocess input vector
        features_dict = {col: traffic_vector.get(col, 0.0) for col in FEATURE_COLUMNS}
        features_df = pd.DataFrame([features_dict])
        
        # Ensure all required columns present and in correct order
        features_df = features_df[FEATURE_COLUMNS]
        
        # Scale features using loaded scaler
        scaled_features = _scaler.transform(features_df)
        
        # 2. Get model prediction (reconstruction) in executor
        loop = asyncio.get_running_loop()
        reconstructed_vector = await loop.run_in_executor(
            None,
            lambda: _model.predict(scaled_features, verbose=0)
        )
        
        # 3. Calculate reconstruction error (Mean Squared Error)
        mse = np.mean(np.power(scaled_features - reconstructed_vector, 2), axis=1)
        reconstruction_error = float(mse[0])
        
        # 4. Compare error to threshold
        is_anomaly = reconstruction_error > _anomaly_threshold
        
        if is_anomaly:
            logger.warning(
                f"Anomaly detected! Reconstruction error: {reconstruction_error:.4f} > "
                f"Threshold: {_anomaly_threshold:.4f}. Vector: {traffic_vector}"
            )
        else:
            logger.debug(
                f"Traffic vector normal. Reconstruction error: {reconstruction_error:.4f} <= "
                f"Threshold: {_anomaly_threshold:.4f}"
            )
        
        return is_anomaly, reconstruction_error
        
    except Exception as e:
        logger.error(f"Error during anomaly detection: {e}", exc_info=True)
        return False, 0.0  # Return non-anomaly on error


def get_model_status() -> dict:
    """Get the status of the ML model."""
    model_path = settings.ML_MODEL_PATH if settings.ML_MODEL_PATH else None
    
    return {
        "loaded": _model_loaded,
        "tensorflow_available": TENSORFLOW_AVAILABLE,
        "model_path": str(model_path) if model_path else None,
        "model_exists": model_path and Path(model_path).exists() if model_path else False,
        "threshold": _anomaly_threshold,
    }
