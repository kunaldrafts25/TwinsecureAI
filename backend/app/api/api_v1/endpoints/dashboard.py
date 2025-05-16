from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.core.dependencies import get_current_active_user
from app.db import crud
from app.db.session import get_db
from app.schemas import (
    AlertSeverityDistribution,
    AlertTrend,
    Attacker,
    AttackVector,
    ComplianceStatus,
    DigitalTwinStatus,
    SecurityMetrics,
    User,
)

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def get_dashboard_data(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get all dashboard data in a single call.
    This is an optimization to reduce the number of API calls needed for the dashboard.
    """
    logger.info(
        f"User {current_user.email} fetching dashboard data for last {days} days"
    )

    try:
        # Get all data in parallel
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
):
    """
    Get security metrics for the dashboard.
    """
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
    # In a real implementation, this would query the database
    # For now, return mock data

    # Get alert counts by severity
    alerts_by_severity = await crud.alert.get_count_by_severity(db)

    # Get alert counts by status
    alerts_by_status = await crud.alert.get_count_by_status(db)

    # Get total alerts
    total_alerts = sum(alerts_by_severity.values())

    # Get top attack vectors
    top_attack_vectors = await get_top_attack_vectors_internal(db, 4, current_user)

    # Get top attackers
    top_attackers = await get_top_attackers_internal(db, 3, current_user)

    # Calculate risk score (this would be more sophisticated in a real implementation)
    # For now, use a simple formula based on alert counts
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


@router.get("/alert-trends", response_model=List[AlertTrend])
async def get_alert_trends(
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get alert trends for the specified number of days.
    """
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
) -> List[AlertTrend]:
    """Internal function to get alert trends."""
    # In a real implementation, this would query the database
    # For now, return mock data

    trends = []
    now = datetime.now()

    for i in range(days, 0, -1):
        date = now - timedelta(days=i)
        date_str = date.strftime("%Y-%m-%d")

        # In a real implementation, these would be actual counts from the database
        trends.append(
            AlertTrend(
                date=date_str,
                critical=min(5, max(0, int((days - i) % 5))),
                high=min(10, max(0, int((days - i) % 10))),
                medium=min(15, max(0, int((days - i) % 15))),
                low=min(10, max(0, int((days - i) % 8))),
                info=min(5, max(0, int((days - i) % 3))),
            )
        )

    return trends


@router.get(
    "/alert-severity-distribution", response_model=List[AlertSeverityDistribution]
)
async def get_alert_severity_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get alert severity distribution for pie chart.
    """
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
) -> List[AlertSeverityDistribution]:
    """Internal function to get alert severity distribution."""
    # In a real implementation, this would query the database
    # For now, return mock data

    # Get alert counts by severity
    alerts_by_severity = await crud.alert.get_count_by_severity(db)

    # Define colors for each severity
    severity_colors = {
        "critical": "#EF4444",
        "high": "#F59E0B",
        "medium": "#FBBF24",
        "low": "#10B981",
        "info": "#3B82F6",
    }

    # Create distribution data
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


@router.get("/attack-vectors", response_model=List[AttackVector])
async def get_top_attack_vectors(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get top attack vectors.
    """
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
) -> List[AttackVector]:
    """Internal function to get top attack vectors."""
    # In a real implementation, this would query the database
    # For now, return mock data

    # Mock attack vectors
    attack_vectors = [
        {"name": "Brute Force", "count": 42, "percentage": 32.8},
        {"name": "SQL Injection", "count": 27, "percentage": 21.1},
        {"name": "Credential Theft", "count": 18, "percentage": 14.1},
        {"name": "XSS", "count": 15, "percentage": 11.7},
        {"name": "Command Injection", "count": 12, "percentage": 9.4},
        {"name": "File Inclusion", "count": 8, "percentage": 6.3},
        {"name": "Path Traversal", "count": 5, "percentage": 3.9},
        {"name": "CSRF", "count": 3, "percentage": 2.3},
    ]

    return [AttackVector(**vector) for vector in attack_vectors[:limit]]


@router.get("/attackers", response_model=List[Attacker])
async def get_top_attackers(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get top attackers.
    """
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
) -> List[Attacker]:
    """Internal function to get top attackers."""
    # In a real implementation, this would query the database
    # For now, return mock data

    # Mock attackers
    now = datetime.now()
    attackers = [
        {
            "ip": "203.0.113.1",
            "country": "US",
            "count": 35,
            "last_seen": (now - timedelta(hours=2)).isoformat(),
        },
        {
            "ip": "198.51.100.2",
            "country": "RU",
            "count": 28,
            "last_seen": (now - timedelta(hours=5)).isoformat(),
        },
        {
            "ip": "192.0.2.3",
            "country": "CN",
            "count": 22,
            "last_seen": (now - timedelta(hours=8)).isoformat(),
        },
        {
            "ip": "198.51.100.4",
            "country": "BR",
            "count": 19,
            "last_seen": (now - timedelta(hours=12)).isoformat(),
        },
        {
            "ip": "203.0.113.5",
            "country": "IN",
            "count": 15,
            "last_seen": (now - timedelta(hours=18)).isoformat(),
        },
        {
            "ip": "192.0.2.6",
            "country": "DE",
            "count": 12,
            "last_seen": (now - timedelta(hours=24)).isoformat(),
        },
        {
            "ip": "198.51.100.7",
            "country": "FR",
            "count": 10,
            "last_seen": (now - timedelta(hours=36)).isoformat(),
        },
        {
            "ip": "203.0.113.8",
            "country": "JP",
            "count": 8,
            "last_seen": (now - timedelta(hours=48)).isoformat(),
        },
    ]

    return [Attacker(**attacker) for attacker in attackers[:limit]]


@router.get("/compliance", response_model=ComplianceStatus)
async def get_compliance_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get compliance status.
    """
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
    # In a real implementation, this would query the database
    # For now, return mock data

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
):
    """
    Get digital twin status.
    """
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
    """Internal function to get digital twin status."""
    # In a real implementation, this would query the database
    # For now, return mock data

    now = datetime.now()

    return DigitalTwinStatus(
        activeTwins=12,
        honeypots=8,
        engagements=24,
        last_engagement=(now - timedelta(hours=3)).isoformat(),
    )


@router.get("/summary", status_code=status.HTTP_200_OK)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """
    Get a summary of the dashboard data for quick overview.
    This is a simplified version of the full dashboard data.
    """
    logger.info(f"User {current_user.email} fetching dashboard summary")

    try:
        # Get security metrics for summary
        security_metrics = await get_security_metrics_internal(db, current_user)

        # Get digital twin status
        digital_twin_status = await get_digital_twin_status_internal(db, current_user)

        # Create a simplified summary
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
