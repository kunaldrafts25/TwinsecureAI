"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Real attack detection service using ML and rule-based systems.
"""

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.db.models.alert import Alert
from app.ml.anomaly_detector import detect_anomaly
from app.services.enrichment import AbuseIPDBClient

class AttackDetector:
    """
    Comprehensive attack detection service combining ML and rule-based detection.
    """
    
    def __init__(self):
        self.anomaly_threshold = 0.05
        self.abuse_score_threshold = 50
        self.rate_limit_threshold = 10  # Alerts per minute from same IP
        self.abuseipdb_client = AbuseIPDBClient()
    
    async def detect_attack(
        self,
        source_ip: str,
        traffic_data: dict,
        db: AsyncSession | None = None
    ) -> tuple[bool, str, float]:
        """
        Detect if traffic represents an attack using multiple methods.
        
        Args:
            source_ip: Source IP address
            traffic_data: Traffic features dictionary
            db: Optional database session for additional checks
            
        Returns:
            Tuple of (is_attack, detection_method, confidence)
        """
        detection_results = []
        
        # 1. ML-based anomaly detection
        try:
            is_anomaly, reconstruction_error = await detect_anomaly(traffic_data)
            if is_anomaly:
                confidence = min(1.0, reconstruction_error * 10)  # Scale to 0-1
                detection_results.append(("ml_anomaly", confidence))
                logger.info(
                    f"ML anomaly detected for {source_ip}: "
                    f"error={reconstruction_error:.4f}"
                )
        except Exception as e:
            logger.warning(f"ML detection failed: {e}")
        
        # 2. AbuseIPDB score check
        try:
            abuse_score = await self.abuseipdb_client.get_abuse_score(source_ip)
            if abuse_score and abuse_score >= self.abuse_score_threshold:
                confidence = min(1.0, abuse_score / 100.0)
                detection_results.append(("abuseipdb", confidence))
                logger.info(f"High abuse score for {source_ip}: {abuse_score}")
        except Exception as e:
            logger.warning(f"AbuseIPDB check failed: {e}")
        
        # 3. Rate-based detection (check recent alerts from same IP)
        if db:
            try:
                recent_alert_count = await self._check_recent_alerts(db, source_ip)
                if recent_alert_count >= self.rate_limit_threshold:
                    confidence = min(
                        1.0, recent_alert_count / (self.rate_limit_threshold * 2)
                    )
                    detection_results.append(("rate_limit", confidence))
                    logger.info(
                        f"Rate limit exceeded for {source_ip}: "
                        f"{recent_alert_count} alerts"
                    )
            except Exception as e:
                logger.warning(f"Rate check failed: {e}")
        
        # 4. Rule-based pattern detection
        pattern_result = self._detect_attack_patterns(traffic_data)
        if pattern_result:
            detection_method, confidence = pattern_result
            detection_results.append((detection_method, confidence))
        
        # Aggregate results
        if detection_results:
            # Use highest confidence detection
            best_detection = max(detection_results, key=lambda x: x[1])
            return True, best_detection[0], best_detection[1]
        
        return False, "none", 0.0
    
    async def _check_recent_alerts(
        self, 
        db: AsyncSession, 
        source_ip: str
    ) -> int:
        """Check number of alerts from same IP in last minute."""
        one_minute_ago = datetime.now(timezone.utc) - timedelta(minutes=1)
        
        stmt = select(func.count(Alert.id)).where(
            Alert.source_ip == source_ip,
            Alert.triggered_at >= one_minute_ago
        )
        
        result = await db.execute(stmt)
        return result.scalar() or 0
    
    def _detect_attack_patterns(self, traffic_data: dict) -> tuple[str, float] | None:
        """
        Detect known attack patterns in traffic data.
        
        Returns:
            Tuple of (pattern_name, confidence) or None
        """
        # Brute force detection (high request frequency)
        request_freq = traffic_data.get('request_freq', 0)
        if request_freq > 100:  # More than 100 requests
            return ("brute_force", min(1.0, request_freq / 200.0))
        
        # SQL injection detection (high entropy in URLs)
        url_entropy = traffic_data.get('url_entropy', 0)
        if url_entropy > 5.0:  # High entropy suggests encoded payloads
            return ("sql_injection", min(1.0, url_entropy / 8.0))
        
        # Port scan detection (many unique IPs connecting)
        unique_ips = traffic_data.get('unique_ips', 0)
        if unique_ips > 50:  # Many different IPs
            return ("port_scan", min(1.0, unique_ips / 100.0))
        
        # DDoS detection (very high request frequency)
        if request_freq > 1000:
            return ("ddos", 0.9)
        
        return None
    
    async def analyze_traffic_batch(
        self,
        traffic_batch: list[dict],
        db: AsyncSession | None = None
    ) -> list[tuple[str, bool, str, float]]:
        """
        Analyze a batch of traffic samples.
        
        Returns:
            List of (source_ip, is_attack, method, confidence) tuples
        """
        results = []
        
        for traffic in traffic_batch:
            source_ip = traffic.get('source_ip', 'unknown')
            is_attack, method, confidence = await self.detect_attack(
                source_ip,
                traffic,
                db
            )
            results.append((source_ip, is_attack, method, confidence))
        
        return results


# Global instance
attack_detector = AttackDetector()


# Convenience function
async def detect_attack_patterns(
    source_ip: str,
    traffic_data: dict,
    db: AsyncSession | None = None
) -> tuple[bool, str, float]:
    """
    Convenience function for attack detection.
    
    Returns:
        Tuple of (is_attack, detection_method, confidence)
    """
    return await attack_detector.detect_attack(source_ip, traffic_data, db)






