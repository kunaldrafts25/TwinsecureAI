"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.
"""

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.core.dependencies import get_current_active_superuser, get_current_active_user
from app.db import crud
from app.db.models import User
from app.db.session import get_db
from app.schemas import Report, ReportGenerationParams, ReportQueryFilters
from app.services.pdf_generator import generate_pdf_report

router = APIRouter()

REPORTS_DIR = Path("storage/reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_model=list[Report])
async def list_reports(
    filters: ReportQueryFilters = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> list[Report]:
    """
    Retrieve a list of generated reports based on query filters.
    Requires authentication.
    """
    logger.info(
        f"User {current_user.email} fetching reports with filters: {filters.model_dump(exclude_none=True)}"
    )
    
    report_list = await crud.report.get_multi(db=db, filters=filters)
    
    for report in report_list:
        if report.file_location:
            report.download_url = f"/api/v1/reports/{report.id}/download"
    
    logger.info(f"Found {len(report_list)} reports matching criteria")
    return report_list


@router.get("/{report_id}", response_model=Report)
async def read_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Report:
    """
    Retrieve metadata for a specific report by its ID.
    Requires authentication.
    """
    logger.info(f"User {current_user.email} fetching report metadata: {report_id}")
    
    report = await crud.report.get(db=db, report_id=report_id)
    
    if not report:
        logger.warning(f"Report not found: {report_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    if report.file_location:
        report.download_url = f"/api/v1/reports/{report.id}/download"
    
    logger.info(f"Report metadata found: {report_id}")
    return report


@router.get("/{report_id}/download")
async def download_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> FileResponse:
    """
    Download the actual report PDF file.
    Requires authentication.
    """
    logger.info(f"User {current_user.email} downloading report: {report_id}")
    
    report = await crud.report.get(db=db, report_id=report_id)
    
    if not report:
        logger.warning(f"Report not found: {report_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    file_path = Path(report.file_location)
    
    if not file_path.exists():
        logger.error(f"Report file not found on disk: {file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found"
        )
    
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name
    )


@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def trigger_report_generation(
    background_tasks: BackgroundTasks,
    params: ReportGenerationParams = Body(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_superuser),
) -> dict[str, str]:
    """
    Trigger the generation of a new report (e.g., weekly summary).
    This runs as a background task. Requires superuser privileges.
    """
    logger.info(
        f"User {current_user.email} triggered report generation with params: {params.model_dump()}"
    )
    
    background_tasks.add_task(
        generate_report_pdf,
        params=params.model_dump(),
        triggered_by_email=current_user.email,
        storage_dir=str(REPORTS_DIR),
    )
    
    logger.info("Report generation task added to background queue")
    return {"message": "Report generation process started in the background"}
