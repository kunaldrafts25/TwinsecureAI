"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

PDF report generation service using ReportLab (local storage only).
"""

import asyncio
import os
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from app.core.config import logger, settings
from app.db import crud
from app.db.models import Alert
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.alert import AlertQueryFilters
from app.schemas.report import Report, ReportCreate

# ReportLab imports
try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )
    
    REPORTLAB_AVAILABLE = True
    logger.info("ReportLab loaded successfully for PDF generation")

except ImportError:
    REPORTLAB_AVAILABLE = False
    logger.error(
        "ReportLab not installed. PDF generation disabled. "
        "Install with: pip install reportlab"
    )


class PDFReportGenerator:
    """
    PDF report generator using ReportLab with local file storage.
    PDFs are stored in the reports/ directory and served via API.
    """
    
    def __init__(self):
        # Use settings if available, otherwise default to 'reports'
        if hasattr(settings, "REPORTS_DIR"):
            self.reports_dir = Path(settings.REPORTS_DIR)
        else:
            self.reports_dir = Path("reports")
        
        # Create directory if it doesn't exist
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"PDF reports will be saved to: {self.reports_dir.absolute()}")
    
    async def generate_report(
        self,
        report_type: str,
        start_time: datetime,
        end_time: datetime,
        db: AsyncSession,
        filters: AlertQueryFilters | None = None
    ) -> Report:
        """
        Generate a security report PDF.
        
        Args:
            report_type: Type of report (security, performance, audit)
            start_time: Report start time
            end_time: Report end time
            db: Database session
            filters: Optional query filters
            
        Returns:
            Report object with local file path
        """
        if not REPORTLAB_AVAILABLE:
            raise RuntimeError("ReportLab not available for PDF generation")
        
        # Create report record
        report_create = ReportCreate(
            report_type=report_type,
            start_time=start_time,
            end_time=end_time,
            status="processing"
        )
        
        report = await crud.report.create(db, obj_in=report_create)
        
        try:
            # Fetch alert data
            alerts_data = await self._fetch_alerts(db, start_time, end_time, filters)
            
            # Calculate aggregates
            aggregates = await self._calculate_aggregates(db, start_time, end_time)
            
            # Generate PDF filename
            filename = f"report_{report.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = self.reports_dir / filename
            
            # Run blocking PDF generation in thread pool
            await asyncio.get_event_loop().run_in_executor(
                None,
                self._generate_pdf,
                str(filepath),
                f"{report_type.title()} Security Report",
                start_time,
                end_time,
                alerts_data,
                aggregates
            )
            
            # Set download URL to API endpoint
            download_url = f"/api/v1/reports/{report.id}/download"
            
            # Update report with file path and status
            report = await crud.report.update(
                db,
                db_obj=report,
                obj_in={
                    "status": "completed",
                    "download_url": download_url,
                    "file_path": str(filepath)  # Store local path
                }
            )
            
            logger.info(f"Report {report.id} generated successfully: {filepath}")
            return report
        
        except Exception as e:
            logger.error(f"Failed to generate report {report.id}: {e}", exc_info=True)
            
            await crud.report.update(
                db,
                db_obj=report,
                obj_in={"status": "failed"}
            )
            
            raise
    
    async def _fetch_alerts(
        self,
        db: AsyncSession,
        start_time: datetime,
        end_time: datetime,
        filters: AlertQueryFilters | None
    ) -> list[Alert]:
        """Fetch alerts for the report period."""
        stmt = select(Alert).where(
            Alert.triggered_at >= start_time,
            Alert.triggered_at <= end_time
        )
        
        if filters:
            if filters.severity:
                stmt = stmt.where(Alert.severity == filters.severity)
            if filters.alert_type:
                stmt = stmt.where(Alert.alert_type == filters.alert_type)
            if filters.source_ip:
                stmt = stmt.where(Alert.source_ip == filters.source_ip)
        
        result = await db.execute(stmt.limit(1000))  # Limit for performance
        return list(result.scalars().all())
    
    async def _calculate_aggregates(
        self,
        db: AsyncSession,
        start_time: datetime,
        end_time: datetime
    ) -> dict:
        """Calculate report statistics and aggregates."""
        stmt = select(Alert).where(
            Alert.triggered_at >= start_time,
            Alert.triggered_at <= end_time
        )
        
        result = await db.execute(stmt)
        alerts = list(result.scalars().all())
        
        # Calculate aggregates
        top_attackers = Counter(alert.source_ip for alert in alerts if alert.source_ip)
        alerts_by_country = Counter(
            alert.location.get("country", "Unknown") 
            for alert in alerts 
            if alert.location
        )
        alerts_by_severity = Counter(alert.severity for alert in alerts)
        alerts_by_type = Counter(alert.alert_type for alert in alerts)
        
        return {
            "total_alerts": len(alerts),
            "top_attackers": top_attackers.most_common(10),
            "alerts_by_country": alerts_by_country.most_common(10),
            "alerts_by_severity": dict(alerts_by_severity),
            "alerts_by_type": dict(alerts_by_type),
        }
    
    def _generate_pdf(
        self,
        filepath: str,
        title: str,
        start_time: datetime,
        end_time: datetime,
        alerts_data: list[Alert],
        aggregates: dict
    ):
        """Synchronous PDF generation using ReportLab."""
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(name="Center", alignment=TA_CENTER, fontSize=14))
        styles.add(ParagraphStyle(name="Right", alignment=TA_RIGHT, fontSize=10))
        
        story = []
        
        # Title
        story.append(Paragraph(title, styles["Title"]))
        story.append(Spacer(1, 0.3 * inch))
        
        # Report metadata
        meta_text = (
            f"<b>Generated:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}<br/>"
            f"<b>Period:</b> {start_time.strftime('%Y-%m-%d %H:%M')} - "
            f"{end_time.strftime('%Y-%m-%d %H:%M')} UTC<br/>"
            f"<b>Total Alerts:</b> {aggregates['total_alerts']}"
        )
        story.append(Paragraph(meta_text, styles["Normal"]))
        story.append(Spacer(1, 0.4 * inch))
        
        # Severity Summary
        if aggregates.get("alerts_by_severity"):
            story.append(Paragraph("Alerts by Severity", styles["Heading2"]))
            
            severity_data = [["Severity", "Count"]]
            for sev, count in aggregates["alerts_by_severity"].items():
                severity_data.append([sev.title(), str(count)])
            
            table = Table(severity_data, colWidths=[3 * inch, 2 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3 * inch))
        
        # Top Attackers
        if aggregates.get("top_attackers"):
            story.append(Paragraph("Top 10 Attacking IPs", styles["Heading2"]))
            
            attacker_data = [["IP Address", "Alert Count"]]
            for ip, count in aggregates["top_attackers"]:
                attacker_data.append([ip, str(count)])
            
            table = Table(attacker_data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3 * inch))
        
        # Geographic Distribution
        if aggregates.get("alerts_by_country"):
            story.append(Paragraph("Top 10 Source Countries", styles["Heading2"]))
            
            country_data = [["Country", "Alert Count"]]
            for country, count in aggregates["alerts_by_country"]:
                country_data.append([country, str(count)])
            
            table = Table(country_data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3 * inch))
        
        # Alert Type Distribution
        if aggregates.get("alerts_by_type"):
            story.append(Paragraph("Alert Types Distribution", styles["Heading2"]))
            
            type_data = [["Alert Type", "Count"]]
            for alert_type, count in aggregates["alerts_by_type"].items():
                type_data.append([alert_type.title(), str(count)])
            
            table = Table(type_data, colWidths=[4 * inch, 2 * inch])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.3 * inch))
        
        # Build PDF
        doc.build(story)
        logger.debug(f"PDF generated: {filepath}")
    
    def get_report_path(self, report_id: UUID) -> Path | None:
        """Get the local file path for a report."""
        # Find report file in reports directory
        for filepath in self.reports_dir.glob(f"report_{report_id}_*.pdf"):
            return filepath
        
        return None


# Global instance
pdf_generator = PDFReportGenerator()


# Convenience function
async def generate_pdf_report(
    report_type: str,
    start_time: datetime,
    end_time: datetime,
    db: AsyncSession,
    filters: AlertQueryFilters | None = None
) -> Report:
    """Convenience function for report generation."""
    return await pdf_generator.generate_report(
        report_type, start_time, end_time, db, filters
    )


# Wrapper function for background task compatibility
async def generate_report_pdf(
    params: dict,
    triggered_by_email: str,
    storage_dir: str
) -> None:
    """
    Wrapper function for background task report generation.
    
    Args:
        params: Report generation parameters
        triggered_by_email: Email of user who triggered the report
        storage_dir: Directory to store the report
    """
    from app.db.session import AsyncSessionLocal
    
    # Parse time range from params
    time_range = params.get("time_range", "last_7_days")
    now = datetime.now(timezone.utc)
    
    if time_range == "last_7_days":
        start_time = now - timedelta(days=7)
        end_time = now
    elif time_range == "last_30_days":
        start_time = now - timedelta(days=30)
        end_time = now
    elif time_range == "last_90_days":
        start_time = now - timedelta(days=90)
        end_time = now
    else:
        # Default to last 7 days
        start_time = now - timedelta(days=7)
        end_time = now
    
    report_type = params.get("report_type", "summary")
    
    # Create filters if severity is specified
    filters = None
    if params.get("severity"):
        filters = AlertQueryFilters(severity=params["severity"])
    
    async with AsyncSessionLocal() as db:
        try:
            await generate_pdf_report(
                report_type=report_type,
                start_time=start_time,
                end_time=end_time,
                db=db,
                filters=filters
            )
            logger.info(f"Report generated successfully by {triggered_by_email}")
        except Exception as e:
            logger.error(f"Error generating report: {e}", exc_info=True)
            raise
