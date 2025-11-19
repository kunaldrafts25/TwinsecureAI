"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import cast, Date, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.core.dependencies import get_current_active_user
from app.db import crud
from app.db.models import Alert, DigitalTwin, TwinEngagement, User
from app.db.session import get_db
from app.schemas import (
    AlertSeverityDistribution,
    AlertTrend,
    Attacker,
    AttackVector,
    ComplianceStatus,
    DigitalTwinStatus,
    SecurityMetrics,
)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_dashboard_data(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Get all dashboard data in a single call.
    Optimization to reduce API calls for dashboard rendering.
    """
    logger.info(
        f"User {current_user.email} fetching dashboard data for last {days} days"
    )
    
    try:
        security_metrics = await get_security_metrics_internal(db, current_user)
        alert_trends = await get_alert_trends_internal(db, days, current_user)
        alert_severity_distribution = await get_alert_severity_distribution_internal(
            db, current_user
        )
        top_attack_vectors = await get_top_attack_vectors_internal(db, 5, current_user)
        top_attackers = await get_top_attackers_internal(db, 5, current_user)
        compliance_status = await get_compliance_status_internal(db, current_user)
        digital_twin_status = await get_digital_twin_status_internal(db, current_user)
        
        return {
            "securityMetrics": security_metrics,
            "alertTrends": alert_trends,
            "alertSeverityDistribution": alert_severity_distribution,
            "topAttackVectors": top_attack_vectors,
            "topAttackers": top_attackers,
            "complianceStatus": compliance_status,
            "digitalTwinStatus": digital_twin_status,
        }
    except Exception as e:
        logger.error(f"Error fetching dashboard data: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data",
        )


@router.get("/security-metrics", response_model=SecurityMetrics)
async def get_security_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SecurityMetrics:
    """Get security metrics for the dashboard."""
    logger.info(f"User {current_user.email} fetching security metrics")
    
    try:
        return await get_security_metrics_internal(db, current_user)
    except Exception as e:
        logger.error(f"Error fetching security metrics: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve security metrics",
        )


async def get_security_metrics_internal(
    db: AsyncSession, current_user: User
) -> SecurityMetrics:
    """Internal function to get security metrics."""
    alerts_by_severity = await crud.alert.get_count_by_severity(db)
    alerts_by_status = await crud.alert.get_count_by_status(db)
    total_alerts = sum(alerts_by_severity.values())
    
    top_attack_vectors = await get_top_attack_vectors_internal(db, 4, current_user)
    top_attackers = await get_top_attackers_internal(db, 3, current_user)
    
    risk_score = min(
        100,
        int(
            (
                alerts_by_severity.get("critical", 0) * 10
                + alerts_by_severity.get("high", 0) * 5
                + alerts_by_severity.get("medium", 0) * 2
            )
            / max(1, total_alerts)
            * 100
        ),
    )
    
    return SecurityMetrics(
        total_alerts=total_alerts,
        alerts_by_severity=alerts_by_severity,
        alerts_by_status=alerts_by_status,
        top_attack_vectors=top_attack_vectors,
        top_attackers=top_attackers,
        risk_score=risk_score,
    )


@router.get("/alert-trends", response_model=list[AlertTrend])
async def get_alert_trends(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[AlertTrend]:
    """Get alert trends for the specified number of days."""
    logger.info(f"User {current_user.email} fetching alert trends for last {days} days")
    
    try:
        return await get_alert_trends_internal(db, days, current_user)
    except Exception as e:
        logger.error(f"Error fetching alert trends: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert trends",
        )


async def get_alert_trends_internal(
    db: AsyncSession, days: int, current_user: User
) -> list[AlertTrend]:
    """Internal function to get alert trends."""
    trends = []
    now = datetime.now(timezone.utc)
    
    for i in range(days, 0, -1):
        date = now - timedelta(days=i)
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date_start + timedelta(days=1)
        date_str = date_start.strftime("%Y-%m-%d")
        
        stmt = (
            select(Alert.severity, func.count(Alert.id).label("count"))
            .where(Alert.triggered_at >= date_start, Alert.triggered_at < date_end)
            .group_by(Alert.severity)
        )
        
        result = await db.execute(stmt)
        rows = result.all()
        
        counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        
        for severity, count in rows:
            if severity:
                severity_str = severity.value if hasattr(severity, "value") else str(severity)
                severity_lower = severity_str.lower()
                if severity_lower in counts:
                    counts[severity_lower] = count
        
        trends.append(
            AlertTrend(
                date=date_str,
                critical=counts["critical"],
                high=counts["high"],
                medium=counts["medium"],
                low=counts["low"],
                info=counts["info"],
            )
        )
    
    return trends


@router.get("/alert-severity-distribution", response_model=list[AlertSeverityDistribution])
async def get_alert_severity_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[AlertSeverityDistribution]:
    """Get alert severity distribution for pie chart."""
    logger.info(f"User {current_user.email} fetching alert severity distribution")
    
    try:
        return await get_alert_severity_distribution_internal(db, current_user)
    except Exception as e:
        logger.error(f"Error fetching alert severity distribution: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alert severity distribution",
        )


async def get_alert_severity_distribution_internal(
    db: AsyncSession, current_user: User
) -> list[AlertSeverityDistribution]:
    """Internal function to get alert severity distribution."""
    alerts_by_severity = await crud.alert.get_count_by_severity(db)
    
    severity_colors = {
        "critical": "#EF4444",
        "high": "#F59E0B",
        "medium": "#FBBF24",
        "low": "#10B981",
        "info": "#3B82F6",
    }
    
    distribution = []
    for severity, count in alerts_by_severity.items():
        distribution.append(
            AlertSeverityDistribution(
                name=severity,
                value=count,
                color=severity_colors.get(severity, "#6B7280"),
            )
        )
    
    return distribution


@router.get("/attack-vectors", response_model=list[AttackVector])
async def get_top_attack_vectors(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[AttackVector]:
    """Get top attack vectors."""
    logger.info(f"User {current_user.email} fetching top {limit} attack vectors")
    
    try:
        return await get_top_attack_vectors_internal(db, limit, current_user)
    except Exception as e:
        logger.error(f"Error fetching top attack vectors: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve top attack vectors",
        )


async def get_top_attack_vectors_internal(
    db: AsyncSession, limit: int, current_user: User
) -> list[AttackVector]:
    """Internal function to get top attack vectors from database."""
    stmt = (
        select(Alert.alert_type, func.count(Alert.id).label("count"))
        .group_by(Alert.alert_type)
        .order_by(func.count(Alert.id).desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    total_stmt = select(func.count(Alert.id))
    total_result = await db.execute(total_stmt)
    total_alerts = total_result.scalar() or 1
    
    attack_vectors = []
    for alert_type, count in rows:
        if alert_type:
            type_str = alert_type.value if hasattr(alert_type, "value") else str(alert_type)
            percentage = (count / total_alerts) * 100 if total_alerts > 0 else 0
            attack_vectors.append(
                {
                    "name": type_str.replace("_", " ").title(),
                    "count": count,
                    "percentage": round(percentage, 1),
                }
            )
    
    return [AttackVector(**vector) for vector in attack_vectors]


@router.get("/attackers", response_model=list[Attacker])
async def get_top_attackers(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[Attacker]:
    """Get top attackers."""
    logger.info(f"User {current_user.email} fetching top {limit} attackers")
    
    try:
        return await get_top_attackers_internal(db, limit, current_user)
    except Exception as e:
        logger.error(f"Error fetching top attackers: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve top attackers",
        )


async def get_top_attackers_internal(
    db: AsyncSession, limit: int, current_user: User
) -> list[Attacker]:
    """Internal function to get top attackers from database."""
    stmt = (
        select(
            Alert.source_ip,
            func.count(Alert.id).label("count"),
            func.max(Alert.triggered_at).label("last_seen"),
        )
        .where(Alert.source_ip.isnot(None))
        .group_by(Alert.source_ip)
        .order_by(func.count(Alert.id).desc())
        .limit(limit)
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    attackers = []
    for source_ip, count, last_seen in rows:
        if source_ip:
            alert_stmt = (
                select(Alert.ip_info)
                .where(Alert.source_ip == source_ip)
                .order_by(Alert.triggered_at.desc())
                .limit(1)
            )
            alert_result = await db.execute(alert_stmt)
            ip_info_row = alert_result.scalar_one_or_none()
            
            country = "Unknown"
            if ip_info_row and isinstance(ip_info_row, dict):
                country = ip_info_row.get("country", "Unknown")
            
            attackers.append(
                {
                    "ip": str(source_ip),
                    "country": country,
                    "count": count,
                    "last_seen": (
                        last_seen.isoformat()
                        if last_seen
                        else datetime.now(timezone.utc).isoformat()
                    ),
                }
            )
    
    return [Attacker(**attacker) for attacker in attackers]


@router.get("/compliance", response_model=ComplianceStatus)
async def get_compliance_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ComplianceStatus:
    """Get compliance status."""
    logger.info(f"User {current_user.email} fetching compliance status")
    
    try:
        return await get_compliance_status_internal(db, current_user)
    except Exception as e:
        logger.error(f"Error fetching compliance status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve compliance status",
        )


async def get_compliance_status_internal(
    db: AsyncSession, current_user: User
) -> ComplianceStatus:
    """Internal function to get compliance status."""
    now = datetime.now()
    
    return ComplianceStatus(
        dpdp={
            "status": "Compliant",
            "compliant": True,
            "last_checked": (now - timedelta(days=5)).isoformat(),
        },
        gdpr={
            "status": "Review needed",
            "compliant": False,
            "last_checked": (now - timedelta(days=10)).isoformat(),
        },
        iso27001={
            "status": "Compliant",
            "compliant": True,
            "last_checked": (now - timedelta(days=15)).isoformat(),
        },
    )


@router.get("/digital-twin", response_model=DigitalTwinStatus)
async def get_digital_twin_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> DigitalTwinStatus:
    """Get digital twin status."""
    logger.info(f"User {current_user.email} fetching digital twin status")
    
    try:
        return await get_digital_twin_status_internal(db, current_user)
    except Exception as e:
        logger.error(f"Error fetching digital twin status: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve digital twin status",
        )


async def get_digital_twin_status_internal(
    db: AsyncSession, current_user: User
) -> DigitalTwinStatus:
    """Internal function to get digital twin status from database."""
    active_twins_stmt = select(func.count(DigitalTwin.id)).where(
        DigitalTwin.status == "active"
    )
    active_twins_result = await db.execute(active_twins_stmt)
    active_twins = active_twins_result.scalar() or 0
    
    honeypots_stmt = select(func.count(DigitalTwin.id)).where(
        DigitalTwin.is_honeypot == True, DigitalTwin.status == "active"
    )
    honeypots_result = await db.execute(honeypots_stmt)
    honeypots = honeypots_result.scalar() or 0
    
    week_ago = datetime.now(timezone.utc) - timedelta(days=7)
    engagements_stmt = select(func.count(TwinEngagement.id)).where(
        TwinEngagement.started_at >= week_ago
    )
    engagements_result = await db.execute(engagements_stmt)
    engagements = engagements_result.scalar() or 0
    
    last_engagement_stmt = select(func.max(TwinEngagement.started_at))
    last_engagement_result = await db.execute(last_engagement_stmt)
    last_engagement_time = last_engagement_result.scalar()
    
    return DigitalTwinStatus(
        activeTwins=active_twins,
        honeypots=honeypots,
        engagements=engagements,
        last_engagement=last_engagement_time.isoformat() if last_engagement_time else None,
    )


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict[str, Any]:
    """
    Get a summary of dashboard data for quick overview.
    Simplified version of full dashboard data.
    """
    logger.info(f"User {current_user.email} fetching dashboard summary")
    
    try:
        security_metrics = await get_security_metrics_internal(db, current_user)
        digital_twin_status = await get_digital_twin_status_internal(db, current_user)
        
        summary = {
            "total_alerts": security_metrics.total_alerts,
            "risk_score": security_metrics.risk_score,
            "critical_alerts": security_metrics.alerts_by_severity.get("critical", 0),
            "high_alerts": security_metrics.alerts_by_severity.get("high", 0),
            "active_twins": digital_twin_status.activeTwins,
            "active_honeypots": digital_twin_status.honeypots,
            "recent_engagements": digital_twin_status.engagements,
            "last_updated": datetime.now().isoformat(),
        }
        
        return summary
    except Exception as e:
        logger.error(f"Error fetching dashboard summary: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard summary",
        )
