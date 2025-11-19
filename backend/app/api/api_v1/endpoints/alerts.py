"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.core.dependencies import get_current_active_superuser, get_current_active_user
from app.db import crud
from app.db.models import User
from app.db.session import get_db
from app.schemas import Alert, AlertCreate, AlertQueryFilters, AlertUpdate
from app.services.alerting.client import alert_client

router = APIRouter()


@router.get("/", response_model=list[Alert])
async def read_alerts(
    filters: AlertQueryFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[Alert]:
    """Retrieve alerts based on query filters. Requires authentication."""
    logger.info(
        f"User {current_user.email} fetching alerts with filters: {filters.model_dump(exclude_none=True)}"
    )
    
    alert_list = await crud.alert.get_multi(db=db, filters=filters)
    logger.info(f"Found {len(alert_list)} alerts matching criteria")
    return alert_list


@router.get("/{alert_id}", response_model=Alert)
async def read_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Alert:
    """Retrieve a specific alert by ID. Requires authentication."""
    logger.info(f"User {current_user.email} fetching alert: {alert_id}")
    
    alert = await crud.alert.get(db=db, alert_id=alert_id)
    
    if not alert:
        logger.warning(f"Alert not found: {alert_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    return alert


@router.post("/", response_model=Alert, status_code=status.HTTP_201_CREATED)
async def create_alert(
    alert_in: AlertCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> Alert:
    """Create new alert manually. Requires superuser privileges."""
    logger.info(
        f"User {current_user.email} creating alert: {alert_in.model_dump(exclude_none=True)}"
    )
    
    alert = await crud.alert.create(db=db, obj_in=alert_in)
    logger.info(f"Alert created: {alert.id}")
    
    # Send notifications asynchronously
    await _send_alert_notification(alert, is_new=True)
    
    return alert


@router.patch("/{alert_id}", response_model=Alert)
async def update_alert(
    alert_id: UUID,
    alert_in: AlertUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Alert:
    """Update existing alert (e.g., change status, add notes). Requires authentication."""
    logger.info(
        f"User {current_user.email} updating alert {alert_id}: {alert_in.model_dump(exclude_unset=True)}"
    )
    
    db_alert = await crud.alert.get(db=db, alert_id=alert_id)
    
    if not db_alert:
        logger.warning(f"Update failed: Alert not found: {alert_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    # Track status change for notifications
    status_changed = (
        alert_in.status is not None
        and alert_in.status != db_alert.status
    )
    
    updated_alert = await crud.alert.update(db=db, db_obj=db_alert, obj_in=alert_in)
    logger.info(f"Alert {alert_id} updated successfully")
    
    # Notify only on status changes
    if status_changed:
        await _send_alert_notification(updated_alert, is_status_change=True)
    
    return updated_alert


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> None:
    """Delete alert. Requires superuser privileges."""
    logger.warning(f"User {current_user.email} deleting alert: {alert_id}")
    
    deleted_alert = await crud.alert.delete(db=db, alert_id=alert_id)
    
    if not deleted_alert:
        logger.error(f"Deletion failed: Alert not found: {alert_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found"
        )
    
    logger.info(f"Alert {alert_id} deleted successfully")


async def _send_alert_notification(
    alert: Alert,
    is_new: bool = False,
    is_status_change: bool = False,
) -> None:
    """Helper function to send alert notifications."""
    try:
        if is_new:
            title = alert.title or f"{alert.severity.value} Alert"
            description = alert.description or "No description provided"
        elif is_status_change:
            title = f"Alert Status Changed: {alert.title or 'Alert'}"
            description = f"Alert status changed to: {alert.status.value}. {alert.description or ''}"
        else:
            return
        
        alert_data = {
            "id": str(alert.id),
            "title": title,
            "severity": alert.severity.value,
            "description": description,
            "source_ip": str(alert.source_ip) if alert.source_ip else None,
            "created_at": alert.created_at.isoformat() if alert.created_at else None,
            "updated_at": alert.updated_at.isoformat() if alert.updated_at else None,
        }
        
        notification_results = await alert_client.send_alert(alert_data=alert_data)
        logger.info(f"Alert notifications sent: {notification_results}")
        
    except Exception as e:
        logger.error(f"Failed to send alert notifications: {str(e)}")
