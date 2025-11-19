"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

ML training pipeline for anomaly detection autoencoder.
"""

import asyncio
import math
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.core.config import logger, settings
from app.db.session import AsyncSessionLocal

ML_TRAINING_DEPENDENCIES_AVAILABLE = True

try:
    import numpy as np  # type: ignore
except Exception as exc:  # pragma: no cover
    ML_TRAINING_DEPENDENCIES_AVAILABLE = False
    np = None  # type: ignore[assignment]
    logger.warning(f"NumPy not available. ML training disabled. Error: {exc}")

try:
    import pandas as pd  # type: ignore
except Exception as exc:  # pragma: no cover
    ML_TRAINING_DEPENDENCIES_AVAILABLE = False
    pd = None  # type: ignore[assignment]
    logger.warning(f"Pandas not available. ML training disabled. Error: {exc}")

try:
    from sklearn.model_selection import train_test_split  # type: ignore
    from sklearn.preprocessing import StandardScaler  # type: ignore
except Exception as exc:  # pragma: no cover
    ML_TRAINING_DEPENDENCIES_AVAILABLE = False
    StandardScaler = None  # type: ignore[assignment]
    train_test_split = None  # type: ignore[assignment]
    logger.warning(f"scikit-learn not available. ML training disabled. Error: {exc}")

# Try to import TensorFlow
try:
    import tensorflow as tf  # type: ignore
    from tensorflow import keras  # type: ignore
    TENSORFLOW_AVAILABLE = True
except Exception as exc:  # pragma: no cover
    TENSORFLOW_AVAILABLE = False
    logger.warning(f"TensorFlow not available. ML training disabled. Error: {exc}")

# Feature columns for training
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


async def fetch_training_data(days: int = 30):
    """
    Fetch 'normal' traffic data from database for training.
    
    Args:
        days: Number of days of historical data to fetch
        
    Returns:
        DataFrame with training features, or None if unavailable
    """
    if not ML_TRAINING_DEPENDENCIES_AVAILABLE or pd is None:
        logger.debug("ML training dependencies missing. Skipping data fetch.")
        return None

    logger.info(f"Fetching training data from last {days} days...")
    
    try:
        async with AsyncSessionLocal() as db:
            from sqlalchemy import select, and_
            from app.db.models import Alert
            
            # Get alerts from last N days that are NOT anomalies
            # Low severity + low abuse score = normal traffic
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            stmt = (
                select(Alert)
                .where(
                    and_(
                        Alert.triggered_at >= cutoff_date,
                        Alert.severity.in_(["low", "info"]),
                        Alert.abuse_score <= 20,
                    )
                )
                .limit(10000)  # Prevent memory issues
            )
            
            result = await db.execute(stmt)
            alerts = result.scalars().all()
            
            if not alerts:
                logger.warning("No training data found in database.")
                return None
            
            logger.info(f"Found {len(alerts)} normal traffic samples.")
            
            # Extract features from alerts
            features_list = []
            for alert in alerts:
                payload = alert.payload or {}
                
                features = {
                    "request_freq": payload.get("request_count", 1),
                    "url_entropy": _calculate_entropy(payload.get("url", "")),
                    "response_time": payload.get("response_time_ms", 0) / 1000.0,
                    "payload_size": len(str(payload)),
                    "status_code_ratio": 1.0 if payload.get("status_code", 200) < 400 else 0.0,
                    "unique_ips": 1,
                    "connection_duration": payload.get("duration_seconds", 0),
                    "bytes_sent": payload.get("bytes_sent", 0),
                    "bytes_received": payload.get("bytes_received", 0),
                    "protocol_type": _encode_protocol(payload.get("protocol", "TCP")),
                }
                features_list.append(features)
            
            df = pd.DataFrame(features_list)
            logger.info(f"Training data: {len(df)} samples, {len(df.columns)} features")
            return df
            
    except Exception as e:
        logger.error(f"Error fetching training data: {e}", exc_info=True)
        return None


def _calculate_entropy(text: str) -> float:
    """Calculate Shannon entropy of a string."""
    if not text:
        return 0.0
    
    counts = Counter(text)
    length = len(text)
    entropy = -sum(
        (count / length) * math.log2(count / length)
        for count in counts.values()
        if count > 0
    )
    return entropy


def _encode_protocol(protocol: str) -> float:
    """Encode protocol as numeric value."""
    protocol_map = {
        "TCP": 1.0,
        "UDP": 2.0,
        "ICMP": 3.0,
        "HTTP": 4.0,
        "HTTPS": 5.0,
    }
    return protocol_map.get(protocol.upper(), 0.0)


async def train_autoencoder_model() -> bool:
    """
    Train TensorFlow Autoencoder on normal traffic data.
    
    Returns:
        True if training successful, False otherwise
    """
    if not TENSORFLOW_AVAILABLE or not ML_TRAINING_DEPENDENCIES_AVAILABLE or np is None or pd is None or StandardScaler is None or train_test_split is None:
        logger.error("ML training dependencies not available. Cannot train.")
        return False
    
    logger.info("Starting ML model training...")
    
    try:
        # 1. Fetch Training Data
        training_df = await fetch_training_data(days=30)
        if training_df is None or training_df.empty:
            logger.warning("No training data. Skipping training.")
            return False
        
        if len(training_df) < 100:
            logger.warning(f"Not enough data ({len(training_df)}). Need >= 100.")
            return False
        
        # 2. Preprocess Data
        if not all(col in training_df.columns for col in FEATURE_COLUMNS):
            logger.error(f"Missing features. Expected: {FEATURE_COLUMNS}")
            return False
        
        features = training_df[FEATURE_COLUMNS].copy()
        features = features.fillna(0.0)
        
        # Scale data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(features)
        
        # 3. Split Data
        X_train, X_test = train_test_split(scaled_data, test_size=0.2, random_state=42)
        
        # 4. Build Autoencoder
        input_dim = X_train.shape[1]
        encoding_dim = max(2, input_dim // 2)
        
        autoencoder = keras.Sequential([
            keras.layers.InputLayer(input_shape=(input_dim,)),
            keras.layers.Dense(encoding_dim * 2, activation="relu"),
            keras.layers.Dense(encoding_dim, activation="relu"),
            keras.layers.Dense(encoding_dim * 2, activation="relu"),
            keras.layers.Dense(input_dim, activation="sigmoid"),
        ])
        
        autoencoder.compile(optimizer="adam", loss="mse", metrics=["mae"])
        logger.info(f"Model: Input={input_dim}, Encoding={encoding_dim}")
        
        # 5. Train
        epochs = getattr(settings, "ML_EPOCHS", 50)
        batch_size = getattr(settings, "ML_BATCH_SIZE", 32)
        
        logger.info(f"Training for {epochs} epochs, batch={batch_size}...")
        autoencoder.fit(
            X_train, X_train,
            epochs=epochs,
            batch_size=batch_size,
            shuffle=True,
            validation_data=(X_test, X_test),
            verbose=1,
        )
        
        # 6. Determine Threshold (95th percentile of reconstruction errors)
        test_reconstructions = autoencoder.predict(X_test, verbose=0)
        mse = np.mean(np.power(X_test - test_reconstructions, 2), axis=1)
        threshold = np.percentile(mse, 95)
        logger.info(f"Anomaly threshold (95th percentile): {threshold:.4f}")
        
        # 7. Save Model
        model_path = Path(settings.ML_MODEL_PATH)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        
        autoencoder.save(str(model_path))
        logger.info(f"Model saved: {model_path}")
        
        # Save scaler
        import joblib
        scaler_path = model_path.parent / "scaler.pkl"
        joblib.dump(scaler, scaler_path)
        logger.info(f"Scaler saved: {scaler_path}")
        
        # Save threshold
        threshold_path = model_path.parent / "threshold.txt"
        threshold_path.write_text(str(threshold))
        logger.info(f"Threshold saved: {threshold_path}")
        
        logger.info("[SUCCESS] ML training completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Training failed: {e}", exc_info=True)
        return False


async def schedule_periodic_training(interval_hours: int = 168) -> None:
    """
    Schedule periodic model retraining (default: weekly).
    
    This should be called as a background task on application startup.
    
    Args:
        interval_hours: Hours between training runs (default 168 = 1 week)
    """
    logger.info(f"Scheduled ML retraining every {interval_hours} hours")
    
    while True:
        try:
            # Wait for interval
            await asyncio.sleep(interval_hours * 3600)
            
            logger.info("Starting scheduled model retraining...")
            success = await train_autoencoder_model()
            
            if success:
                logger.info("[SUCCESS] Scheduled retraining successful")
            else:
                logger.warning("[WARNING] Scheduled retraining failed")
                
        except asyncio.CancelledError:
            logger.info("Periodic training task cancelled")
            break
        except Exception as e:
            logger.error(f"Error in periodic training: {e}", exc_info=True)
            # Continue running even if one training fails


# Entry point for manual training
if __name__ == "__main__":
    asyncio.run(train_autoencoder_model())
