#!/usr/bin/env python3
"""
TwinSecure - ML Model Training Script

This script trains the anomaly detection autoencoder model.
It can be run standalone or triggered via API.

Usage:
    python scripts/train_ml_model.py
    python scripts/train_ml_model.py --days 60  # Use 60 days of data
    python scripts/train_ml_model.py --epochs 100  # Train for 100 epochs
"""

import asyncio
import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set minimal environment variables if not set (to avoid config errors)
# Set to valid JSON arrays for list types (pydantic-settings expects JSON for lists)
if "BACKEND_CORS_ORIGINS" not in os.environ or os.environ.get("BACKEND_CORS_ORIGINS", "").strip() == "":
    os.environ["BACKEND_CORS_ORIGINS"] = "[]"
if "ALERT_RECIPIENTS" not in os.environ or os.environ.get("ALERT_RECIPIENTS", "").strip() == "":
    os.environ["ALERT_RECIPIENTS"] = "[]"
if "JWT_BLACKLIST_TOKEN_CHECKS" not in os.environ:
    os.environ["JWT_BLACKLIST_TOKEN_CHECKS"] = '["access", "refresh"]'
# Set ML_MODEL_PATH if not set
if "ML_MODEL_PATH" not in os.environ:
    os.environ["ML_MODEL_PATH"] = "models/anomaly_detector.h5"
# Set required database password if not set
if "POSTGRES_PASSWORD" not in os.environ:
    os.environ["POSTGRES_PASSWORD"] = "postgres"
if "FIRST_SUPERUSER_PASSWORD" not in os.environ:
    os.environ["FIRST_SUPERUSER_PASSWORD"] = "admin123"

from app.core.config import settings
from app.ml.training import train_autoencoder_model, fetch_training_data
from app.core.config import logger


async def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train ML anomaly detection model")
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days of historical data to use (default: 30)",
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Number of training epochs (overrides config)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Batch size for training (overrides config)",
    )
    parser.add_argument(
        "--check-data-only",
        action="store_true",
        help="Only check if training data is available, don't train",
    )
    
    args = parser.parse_args()
    
    # Override config if provided
    if args.epochs:
        settings.ML_EPOCHS = args.epochs
    if args.batch_size:
        settings.ML_BATCH_SIZE = args.batch_size
    
    # Check ML_MODEL_PATH is configured
    if not settings.ML_MODEL_PATH:
        logger.error("ML_MODEL_PATH not configured in environment variables!")
        logger.error("Please set ML_MODEL_PATH in your .env file")
        logger.error("Example: ML_MODEL_PATH=models/anomaly_detector.h5")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("ML Model Training Script")
    logger.info("=" * 60)
    logger.info(f"Model path: {settings.ML_MODEL_PATH}")
    logger.info(f"Training data: Last {args.days} days")
    logger.info(f"Epochs: {settings.ML_EPOCHS}")
    logger.info(f"Batch size: {settings.ML_BATCH_SIZE}")
    logger.info("=" * 60)
    
    # Check if we only want to verify data
    if args.check_data_only:
        logger.info("Checking training data availability...")
        training_df = await fetch_training_data(days=args.days)
        if training_df is None or training_df.empty:
            logger.warning("[ERROR] No training data found!")
            sys.exit(1)
        logger.info(f"[SUCCESS] Found {len(training_df)} training samples")
        logger.info(f"   Features: {list(training_df.columns)}")
        sys.exit(0)
    
    # Run training
    logger.info("Starting training...")
    success = await train_autoencoder_model()
    
    if success:
        logger.info("=" * 60)
        logger.info("[SUCCESS] Training completed successfully!")
        logger.info(f"Model saved to: {settings.ML_MODEL_PATH}")
        logger.info("=" * 60)
        sys.exit(0)
    else:
        logger.error("=" * 60)
        logger.error("[FAILED] Training failed!")
        logger.error("Check logs above for details")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

