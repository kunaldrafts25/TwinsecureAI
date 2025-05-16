from typing import List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.core.dependencies import get_current_active_superuser, get_current_active_user
from app.db import crud
from app.db.models import User
from app.db.session import get_db
from app.schemas import Report, ReportCreate, ReportQueryFilters, ReportUpdate
from app.services.alerting.client import alert_client

# Import PDF generation service and alerting
from app.services.pdf_generator import generate_report_pdf  # Placeholder function

router = APIRouter()


@router.get("/list", response_model=List[Report])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    filters: ReportQueryFilters = Depends(),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve a list of generated reports based on query filters.
    Requires authentication.
    """
    logger.info(
        f"User {current_user.email} fetching reports list with filters: {filters.model_dump(exclude_none=True)}"
    )
    reports = await crud.report.get_multi(db=db, filters=filters)
    # TODO: Construct download URLs if needed (e.g., presigned S3 URLs)
    logger.info(f"Found {len(reports)} reports matching criteria.")
    return reports


@router.get("/{report_id}", response_model=Report)
async def read_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Retrieve metadata for a specific report by its ID.
    Requires authentication.
    """
    logger.info(
        f"User {current_user.email} fetching report metadata for ID: {report_id}"
    )
    db_report = await crud.report.get(db=db, report_id=report_id)
    if db_report is None:
        logger.warning(f"Report metadata not found: {report_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Report not found"
        )
    # TODO: Construct download URL
    logger.info(f"Report metadata found: {report_id}")
    return db_report


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def trigger_report_generation(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(
        get_db
    ),  # May not be needed directly if task handles DB interaction
    current_user: User = Depends(
        get_current_active_superuser
    ),  # Restrict who can trigger generation
    # Add parameters for report generation if needed (e.g., time range, specific filters)
    # report_params: ReportGenerationParams = Body(...)
):
    """
    Trigger the generation of a new report (e.g., weekly summary).
    This runs as a background task. Requires superuser privileges.
    (This could also be triggered by a scheduled job/cron).
    """
    logger.info(f"User {current_user.email} triggered report generation.")

    # Define parameters for the report (can come from request body or defaults)
    generation_params = {
        "time_range": "last_7_days",
        "triggered_by": current_user.email,
    }

    # Add the PDF generation function to background tasks
    # Pass necessary parameters, including potentially the DB session factory or connection string
    # if the background task needs its own session.
    background_tasks.add_task(
        generate_report_pdf,
        params=generation_params,
        # db_url=str(settings.DATABASE_URL) # Pass URL if task needs new session
    )

    logger.info("Report generation task added to background queue.")
    return {"message": "Report generation process started in the background."}


# Note: The actual report generation logic (generate_report_pdf) lives in app/services/pdf_generator.py
# It would fetch data, format it, create a PDF, store it (e.g., S3),
# create a Report record in the DB, and potentially send notifications.

# Optional: Add GET endpoint for downloading the actual PDF file
# This would typically involve fetching the file from storage (S3) and returning a FileResponse or StreamingResponse.
# @router.get("/{report_id}/download")
# async def download_report_file(...) -> FileResponse: ...

# Optional: Add DELETE endpoint for reports (requires permissions)
