"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.
"""

import math
from collections import Counter
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger, settings
from app.db import crud
from app.db.session import get_db
from app.schemas import AlertCreate, HoneypotData
from app.services.alerting.client import alert_client
from app.services.attack_detection import attack_detector
from app.services.attack_response import respond_to_attack
from app.services.enrichment import check_ip_reputation, get_ip_location
from app.services.validation import validate_ip_address

router = APIRouter()


def _calculate_severity(is_attack: bool, confidence: float, abuse_score: int | None) -> str:
    """Calculate alert severity based on detection results."""
    if is_attack:
        if confidence > 0.8 or (abuse_score and abuse_score > 80):
            return "critical"
        elif confidence > 0.6 or (abuse_score and abuse_score > 60):
            return "high"
        else:
            return "medium"
    elif abuse_score and abuse_score > 50:
        return "medium"
    return "low"


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
        "HTTPS": 5.0
    }
    return protocol_map.get(protocol.upper(), 0.0)


async def process_honeypot_data(db: AsyncSession, data: HoneypotData) -> None:
    """
    Background task to process honeypot data: enrich, detect attacks, respond, store, alert.
    """
    logger.info(f"Processing honeypot data for IP: {data.source_ip}")
    
    ip_str = str(data.source_ip)
    
    if not validate_ip_address(ip_str):
        logger.warning(f"Invalid IP address format: {ip_str}")
        return
    
    alert_payload = data.model_dump()
    
    try:
        ip_info = await get_ip_location(ip_str)
        abuse_result = await check_ip_reputation(ip_str)
        abuse_score = abuse_result.get("abuseConfidencePercentage", 0) if abuse_result else 0
        logger.debug(f"Enrichment for {ip_str}: Geo={ip_info}, AbuseScore={abuse_score}")
        
        traffic_features = {
            "request_freq": alert_payload.get("request_count", 1),
            "url_entropy": _calculate_entropy(alert_payload.get("url", "")),
            "response_time": alert_payload.get("response_time_ms", 0) / 1000.0,
            "payload_size": len(str(alert_payload)),
            "status_code_ratio": 1.0 if alert_payload.get("status_code", 200) < 400 else 0.0,
            "unique_ips": 1,
            "connection_duration": alert_payload.get("duration_seconds", 0),
            "bytes_sent": alert_payload.get("bytes_sent", 0),
            "bytes_received": alert_payload.get("bytes_received", 0),
            "protocol_type": _encode_protocol(alert_payload.get("protocol", "TCP")),
            "source_ip": ip_str,
        }
        
        is_attack, detection_method, confidence = await attack_detector.detect_attack(
            source_ip=ip_str,
            traffic_data=traffic_features,
            db=db
        )
        
        severity = _calculate_severity(is_attack, confidence, abuse_score)
        
        alert_in = AlertCreate(
            alert_type="Honeypot Triggered" if not is_attack else f"Attack Detected: {detection_method}",
            source_ip=data.source_ip,
            ip_info=ip_info,
            payload={
                **alert_payload,
                "traffic_features": traffic_features,
                "detection_method": detection_method,
                "confidence": confidence
            },
            abuse_score=abuse_score,
            severity=severity,
            status="new",
            triggered_at=data.timestamp,
        )
        
        created_alert = await crud.alert.create(db=db, obj_in=alert_in)
        logger.info(
            f"Honeypot alert created: ID={created_alert.id}, IP={ip_str}, "
            f"Attack={is_attack}, Method={detection_method}, Confidence={confidence:.2%}"
        )
        
        if is_attack:
            response_actions = await attack_response.respond_to_attack(
                source_ip=ip_str,
                attack_type=detection_method,
                severity=severity,
                confidence=confidence,
                alert_id=str(created_alert.id),
                db=db
            )
            logger.info(f"Automated response for {ip_str}: {response_actions}")
        
        await alert_client.send_alert(
            alert_data={
                "id": str(created_alert.id),
                "title": created_alert.title or f"{severity.upper()} Alert",
                "severity": severity,
                "description": f"Honeypot triggered by {ip_str}. Detection: {detection_method}, Confidence: {confidence:.2%}",
                "source_ip": ip_str,
                "created_at": created_alert.created_at.isoformat() if created_alert.created_at else None,
            }
        )
        logger.info(f"External alert sent for honeypot trigger from {ip_str}")
        
    except Exception as e:
        logger.error(f"Error processing honeypot data for {ip_str}: {e}", exc_info=True)
        
        try:
            error_alert = AlertCreate(
                alert_type="Honeypot Processing Error",
                source_ip=data.source_ip,
                payload={"error": str(e), "original_data": alert_payload},
                severity="high",
                status="new",
                triggered_at=data.timestamp,
            )
            await crud.alert.create(db=db, obj_in=error_alert)
        except Exception as db_err:
            logger.error(f"CRITICAL: Failed to log honeypot error to DB: {db_err}")


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def receive_honeypot_trigger(
    request: Request,
    honeypot_data: HoneypotData,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Receives mirrored traffic data (e.g., from AWS WAF logs via Kinesis/Lambda).
    Validates input and triggers background processing for enrichment, detection, and alerting.
    """
    expected_secret = getattr(settings, "HONEYPOT_SECRET_HEADER", None)
    if expected_secret:
        received_secret = request.headers.get("X-TwinSecure-Honeypot-Secret")
        if not received_secret or received_secret != expected_secret:
            client_host = request.client.host if request.client else "unknown"
            logger.warning(f"Unauthorized honeypot access from {client_host}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid or missing secret header"
            )
    
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"Received honeypot trigger from {client_ip} for source IP: {honeypot_data.source_ip}")
    
    background_tasks.add_task(process_honeypot_data, db, honeypot_data)
    logger.debug("Honeypot data processing added to background queue")
    
    return {
        "message": "Honeypot data received and queued for processing",
        "client_ip": client_ip,
    }
