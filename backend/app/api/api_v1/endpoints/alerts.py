from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from app.core.dependencies import get_current_active_superuser
from app.db import crud
from app.db.session import get_db
from app.schemas import Alert, AlertCreate, AlertUpdate, AlertQueryFilters
from app.db.models import User # Import User model for dependency
from app.core.dependencies import get_current_active_user # Or get_current_active_superuser if needed
from app.core.config import logger
# Import alerting services if triggering alerts from here (less common for GET/PATCH)
# from app.services.alerting.client import alert_client

router = APIRouter()

@router.get("/", response_model=List[Alert])
async def read_alerts(
    db: AsyncSession = Depends(get_db),
    # Use Depends(AlertQueryFilters) to automatically parse query params into the schema
    filters: AlertQueryFilters = Depends(),
    current_user: User = Depends(get_current_active_user), # Ensure user is logged in
):
    """
    Retrieve a list of alerts based on query filters.
    Requires authentication.
    """
    logger.info(f"User {current_user.email} fetching alerts with filters: {filters.model_dump(exclude_none=True)}")
    alerts = await crud.alert.get_multi(db=db, filters=filters)
    logger.info(f"Found {len(alerts)} alerts matching criteria.")
    return alerts

@router.get("/{alert_id}", response_model=Alert)
async def read_alert(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve a specific alert by its ID.
    Requires authentication.
    """
    logger.info(f"User {current_user.email} fetching alert with ID: {alert_id}")
    db_alert = await crud.alert.get(db=db, alert_id=alert_id)
    if db_alert is None:
        logger.warning(f"Alert not found: {alert_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    logger.info(f"Alert found: {alert_id}")
    return db_alert

# POST endpoint might be less common here if alerts are created by honeypot/ML module
# But could be used for manual alert creation if needed.
@router.post("/", response_model=Alert, status_code=status.HTTP_201_CREATED)
async def create_alert(
    *,
    db: AsyncSession = Depends(get_db),
    alert_in: AlertCreate,
    current_user: User = Depends(get_current_active_superuser), # Require superuser to create alerts manually?
):
    """
    Create a new alert manually (requires appropriate permissions).
    """
    logger.info(f"User {current_user.email} attempting to create alert: {alert_in.model_dump(exclude_none=True)}")
    alert = await crud.alert.create(db=db, obj_in=alert_in)
    logger.info(f"Alert created successfully with ID: {alert.id}")
    # Optionally trigger notifications here if manual creation should also alert
    # await alert_client.send_alert(alert_data=alert)
    return alert

@router.patch("/{alert_id}", response_model=Alert)
async def update_alert(
    *,
    db: AsyncSession = Depends(get_db),
    alert_id: UUID,
    alert_in: AlertUpdate,
    current_user: User = Depends(get_current_active_user), # Allow analysts to update status/notes
):
    """
    Update an existing alert (e.g., change status, add notes).
    Requires authentication.
    """
    logger.info(f"User {current_user.email} attempting to update alert {alert_id} with data: {alert_in.model_dump(exclude_unset=True)}")
    db_alert = await crud.alert.get(db=db, alert_id=alert_id)
    if not db_alert:
        logger.warning(f"Update failed: Alert not found: {alert_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")

    updated_alert = await crud.alert.update(db=db, db_obj=db_alert, obj_in=alert_in)
    logger.info(f"Alert {alert_id} updated successfully.")
    return updated_alert

# Optional: Add DELETE endpoint if needed (requires permissions)
# @router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_alert(
#     *,
#     db: AsyncSession = Depends(get_db),
#     alert_id: UUID,
#     current_user: User = Depends(get_current_active_superuser), # Usually restricted
# ):
#     """
#     Delete an alert. Requires superuser privileges.
#     """
#     logger.warning(f"User {current_user.email} attempting to delete alert {alert_id}")
#     deleted_alert = await crud.alert.delete(db=db, alert_id=alert_id)
#     if not deleted_alert:
#         logger.error(f"Deletion failed: Alert not found: {alert_id}")
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
#     logger.info(f"Alert {alert_id} deleted successfully.")
#     return Response(status_code=status.HTTP_204_NO_CONTENT)