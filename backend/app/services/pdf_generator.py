"""
TwinSecure - Advanced Cybersecurity Platform
Copyright © 2024 TwinSecure. All rights reserved.

This file is part of TwinSecure, a proprietary cybersecurity platform.
Unauthorized copying, distribution, modification, or use of this software
is strictly prohibited without explicit written permission.

For licensing inquiries: kunalsingh2514@gmail.com
"""

import asyncio  # For running blocking IO in thread
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import logger, settings
from app.db import crud
from app.db.session import AsyncSessionLocal
from app.schemas import AlertQueryFilters, Report, ReportCreate  # Import Report schema

# --- PDF Library Selection ---
# Choose ONE library and ensure it and its dependencies are installed.
PDF_LIBRARY = "reportlab"  # Options: "reportlab", "weasyprint", "pdfkit"

if PDF_LIBRARY == "reportlab":
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
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

        logger.info("Using ReportLab for PDF generation.")
    except ImportError:
        logger.error(
            "ReportLab not installed. PDF generation will fail. Install with 'pip install reportlab'"
        )
        PDF_LIBRARY = None
elif PDF_LIBRARY == "weasyprint":
    try:
        import weasyprint

        # Requires system dependencies: Pango, Cairo, GDK-PixBuf
        logger.info("Using WeasyPrint for PDF generation.")
    except ImportError:
        logger.error(
            "WeasyPrint not installed or system dependencies missing. PDF generation will fail. Install with 'pip install weasyprint' and ensure system libs are present."
        )
        PDF_LIBRARY = None
elif PDF_LIBRARY == "pdfkit":
    try:
        import pdfkit

        # Requires wkhtmltopdf executable installed and in PATH or configured
        logger.info("Using pdfkit for PDF generation.")
    except ImportError:
        logger.error(
            "pdfkit not installed or wkhtmltopdf not found. PDF generation will fail. Install with 'pip install pdfkit' and ensure wkhtmltopdf is installed."
        )
        PDF_LIBRARY = None
else:
    logger.error(
        f"Invalid PDF_LIBRARY selected: {PDF_LIBRARY}. PDF generation disabled."
    )
    PDF_LIBRARY = None


# --- Placeholder for file storage (e.g., S3) ---
# import boto3
# s3_client = None
# if settings.AWS_REGION: # Basic check if AWS might be configured
#     try:
#         s3_client = boto3.client('s3', region_name=settings.AWS_REGION)
#         logger.info("S3 client initialized for PDF storage.")
#     except ImportError:
#         logger.warning("boto3 not installed. S3 upload for reports disabled.")
#     except Exception as e:
#         logger.error(f"Failed to initialize S3 client: {e}")


def _generate_pdf_reportlab(
    filename: str,
    title: str,
    start_time: datetime,
    end_time: datetime,
    alerts_data: list,
    aggregates: dict,
):
    """Synchronous function to generate PDF using ReportLab."""
    doc = SimpleDocTemplate(filename)
    styles = getSampleStyleSheet()
    # Custom styles
    styles.add(ParagraphStyle(name="Justify", alignment=TA_LEFT))
    styles.add(ParagraphStyle(name="Center", alignment=TA_CENTER))
    styles.add(ParagraphStyle(name="Code", fontName="Courier", fontSize=8, leading=9))

    story = []

    # Title
    story.append(Paragraph(title, styles["h1"]))
    story.append(Spacer(1, 0.2 * inch))

    # Summary Section
    story.append(Paragraph("Report Summary", styles["h2"]))
    summary_text = f"""
    This report covers security events detected by TwinSecure AI between
    {start_time.strftime('%Y-%m-%d %H:%M:%S UTC')} and {end_time.strftime('%Y-%m-%d %H:%M:%S UTC')}.<br/><br/>
    <b>Total alerts analyzed: {len(alerts_data)}</b>
    """
    story.append(Paragraph(summary_text, styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    # Top Attackers Section
    if aggregates.get("top_attackers"):
        story.append(Paragraph("Top 10 Attacking IPs", styles["h2"]))
        table_data = [["IP Address", "Alert Count"]]
        for ip, count in aggregates["top_attackers"][:10]:
            table_data.append([ip, str(count)])
        t = Table(table_data, colWidths=[3 * inch, 1 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

    # Alerts by Country Section
    if aggregates.get("alerts_by_country"):
        story.append(Paragraph("Top 10 Source Countries", styles["h2"]))
        table_data = [["Country", "Alert Count"]]
        for country, count in aggregates["alerts_by_country"][:10]:
            table_data.append([country, str(count)])
        t = Table(table_data, colWidths=[3 * inch, 1 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(t)
        story.append(Spacer(1, 0.2 * inch))

    # Add more sections (Alert Types, Severity, etc.) using similar patterns
    # Example: Alert Details Snippet (use carefully)
    # story.append(Paragraph("Sample Alert Details", styles['h2']))
    # for alert in alerts_data[:3]: # Show first 3 alerts
    #     alert_detail = f"<b>ID:</b> {alert.id}<br/><b>Type:</b> {alert.alert_type}<br/><b>IP:</b> {alert.source_ip}<br/><b>Time:</b> {alert.triggered_at.strftime('%Y-%m-%d %H:%M')}<br/>"
    #     if alert.payload:
    #         payload_str = str(alert.payload)[:100] + "..."
    #         alert_detail += f"<b>Payload:</b><br/><para style='Code'>{payload_str}</para>"
    #     story.append(Paragraph(alert_detail, styles['Normal']))
    #     story.append(Spacer(1, 0.1*inch))

    # Recommendations Section
    story.append(Paragraph("Recommendations", styles["h2"]))
    recommendations = aggregates.get(
        "recommendations", "No specific recommendations generated."
    )
    story.append(Paragraph(recommendations, styles["Normal"]))

    # Build the PDF
    doc.build(story)


def _generate_pdf_weasyprint(filename: str, html_content: str):
    """Synchronous function to generate PDF using WeasyPrint."""
    # Requires html_content as input
    css = weasyprint.CSS(
        string="""
        @page { size: A4; margin: 1in; }
        body { font-family: sans-serif; }
        h1, h2 { text-align: center; color: #333; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 1em;}
        th, td { border: 1px solid #ccc; padding: 0.3em; text-align: left;}
        th { background-color: #eee; font-weight: bold;}
        pre { background-color: #f8f8f8; border: 1px solid #ddd; padding: 0.5em; white-space: pre-wrap; word-wrap: break-word; }
    """
    )
    weasyprint.HTML(string=html_content).write_pdf(filename, stylesheets=[css])


def _generate_pdf_pdfkit(filename: str, html_content: str):
    """Synchronous function to generate PDF using pdfkit."""
    # Requires html_content as input
    # Configure path to wkhtmltopdf if not in PATH
    # config = pdfkit.configuration(wkhtmltopdf='/path/to/wkhtmltopdf')
    # pdfkit.from_string(html_content, filename, configuration=config)
    options = {
        "page-size": "A4",
        "margin-top": "1.0in",
        "margin-right": "1.0in",
        "margin-bottom": "1.0in",
        "margin-left": "1.0in",
        "encoding": "UTF-8",
        "enable-local-file-access": None,  # Be cautious with this option
    }
    pdfkit.from_string(html_content, filename, options=options)


async def _upload_to_s3(local_path: str, s3_key: str) -> Optional[str]:
    """Placeholder for uploading file to S3."""
    # if not s3_client: return None
    # bucket_name = 'twinsecure-reports' # Get from settings
    # try:
    #     s3_client.upload_file(local_path, bucket_name, s3_key)
    #     uri = f"s3://{bucket_name}/{s3_key}"
    #     logger.info(f"Report uploaded to S3: {uri}")
    #     return uri
    # except Exception as e:
    #     logger.error(f"Failed to upload report {local_path} to S3 ({bucket_name}/{s3_key}): {e}")
    #     return None
    logger.warning(f"S3 upload skipped. Using local file path for {local_path}")
    return f"file://{local_path}"  # Return local URI if S3 fails or is disabled


async def generate_report_pdf(params: dict):
    """
    Generates a PDF report based on given parameters, running blocking IO in threads.

    Args:
        params: Dictionary containing parameters like time_range, filters, triggered_by.
    """
    if not PDF_LIBRARY:
        logger.error(
            "No valid PDF library configured or available. Cannot generate report."
        )
        return

    logger.info(f"Starting PDF report generation with params: {params}")
    generation_start_time = datetime.now(timezone.utc)

    # --- Define Report Scope ---
    report_end_time = datetime.now(timezone.utc)
    report_start_time = report_end_time - timedelta(days=7)  # Default
    time_range_str = params.get("time_range", "last_7_days")
    if time_range_str == "last_24_hours":
        report_start_time = report_end_time - timedelta(days=1)
    # Add more time range options...

    report_title = f"TwinSecure Security Summary ({report_start_time.strftime('%Y-%m-%d')} to {report_end_time.strftime('%Y-%m-%d')})"
    filename_ts = generation_start_time.strftime("%Y%m%d-%H%M%S")
    filename = f"twinsecure-report-{filename_ts}.pdf"
    local_pdf_path = f"/tmp/{filename}"  # Ensure /tmp is writable in container

    # --- Fetch and Aggregate Data ---
    alerts_data = []
    aggregates = {}
    try:
        async with AsyncSessionLocal() as db:
            alert_filters = AlertQueryFilters(
                start_time=report_start_time,
                end_time=report_end_time,
                limit=1000,  # Limit alerts for report performance
            )
            alerts_data = await crud.alert.get_multi(db=db, filters=alert_filters)
            logger.info(f"Fetched {len(alerts_data)} alerts for the report period.")

            # --- Perform Aggregations ---
            top_attackers = {}
            alerts_by_country = {}
            for alert in alerts_data:
                ip = str(alert.source_ip)
                if ip:
                    top_attackers[ip] = top_attackers.get(ip, 0) + 1
                country = alert.ip_info.get("country") if alert.ip_info else "Unknown"
                alerts_by_country[country] = alerts_by_country.get(country, 0) + 1

            aggregates["top_attackers"] = sorted(
                top_attackers.items(), key=lambda item: item[1], reverse=True
            )
            aggregates["alerts_by_country"] = sorted(
                alerts_by_country.items(), key=lambda item: item[1], reverse=True
            )
            # Add more aggregations...

            # --- Generate Recommendations (Example) ---
            recs = []
            if aggregates["top_attackers"]:
                recs.append(
                    f"- Review activity from top attacking IPs: {', '.join([ip for ip, count in aggregates['top_attackers'][:3]])}."
                )
                # Consider threshold for blocking recommendation
                if (
                    aggregates["top_attackers"][0][1] > 50
                ):  # If top attacker has > 50 alerts
                    recs.append(
                        f"- Consider blocking IP {aggregates['top_attackers'][0][0]} due to high alert volume ({aggregates['top_attackers'][0][1]} alerts)."
                    )
            if aggregates["alerts_by_country"]:
                recs.append(
                    f"- Monitor traffic from top source countries: {', '.join([c for c, count in aggregates['alerts_by_country'][:3]])}."
                )
            aggregates["recommendations"] = (
                "\n".join(recs) if recs else "No specific automated recommendations."
            )

    except Exception as e:
        logger.error(
            f"Error fetching/aggregating data for PDF report: {e}", exc_info=True
        )
        return

    # --- Generate PDF Content (Run blocking PDF generation in thread) ---
    pdf_generation_successful = False
    loop = asyncio.get_running_loop()
    try:
        if PDF_LIBRARY == "reportlab":
            await loop.run_in_executor(
                None,
                _generate_pdf_reportlab,
                local_pdf_path,
                report_title,
                report_start_time,
                report_end_time,
                alerts_data,
                aggregates,
            )
            pdf_generation_successful = True
        elif PDF_LIBRARY in ["weasyprint", "pdfkit"]:
            # These libraries often work better with HTML input
            # TODO: Create an HTML template (e.g., using Jinja2) and render it
            html_content = f"<h1>{report_title}</h1><p>PDF generation using {PDF_LIBRARY} needs HTML template implementation.</p>"  # Placeholder HTML
            if PDF_LIBRARY == "weasyprint":
                await loop.run_in_executor(
                    None, _generate_pdf_weasyprint, local_pdf_path, html_content
                )
                pdf_generation_successful = True
            elif PDF_LIBRARY == "pdfkit":
                await loop.run_in_executor(
                    None, _generate_pdf_pdfkit, local_pdf_path, html_content
                )
                pdf_generation_successful = True

        if pdf_generation_successful:
            logger.info(
                f"PDF report generated successfully using {PDF_LIBRARY} at: {local_pdf_path}"
            )
        else:
            logger.error("PDF generation skipped due to library configuration issue.")
            return  # Exit if PDF wasn't generated

    except Exception as e:
        logger.error(
            f"Error generating PDF content with {PDF_LIBRARY}: {e}", exc_info=True
        )
        if os.path.exists(local_pdf_path):
            os.remove(local_pdf_path)  # Clean up partial file
        return  # Stop processing

    # --- Store PDF and Update Database ---
    file_location_uri = None
    created_report_model = None
    try:
        # Placeholder: Upload local_pdf_path to S3 or other storage
        s3_key = f"reports/{filename}"  # Define S3 key structure
        file_location_uri = await _upload_to_s3(local_pdf_path, s3_key)

        if not file_location_uri:
            raise RuntimeError("Failed to store PDF report.")  # Or handle differently

        # --- Create Report Record in DB ---
        async with AsyncSessionLocal() as db:
            report_in = ReportCreate(
                title=report_title,
                summary=f"Analyzed {len(alerts_data)} alerts. Top attacker IP: {aggregates['top_attackers'][0][0] if aggregates.get('top_attackers') else 'N/A'}.",
                filename=filename,
                file_location=file_location_uri,  # Store S3 URI or final path
                generation_params=params,
                recommendations=aggregates.get("recommendations"),
                generated_at=generation_start_time,
            )
            created_report = await crud.report.create(db=db, obj_in=report_in)
            # Convert DB model to Pydantic model for notification
            created_report_model = Report.model_validate(created_report)
            logger.info(
                f"Report record created in database with ID: {created_report.id}"
            )

    except Exception as e:
        logger.error(f"Error storing PDF or updating database: {e}", exc_info=True)
        # Consider cleanup (e.g., delete uploaded S3 object if DB entry failed?)
        return  # Stop if DB update failed

    # --- Send Notification ---
    if created_report_model:
        try:
            report_notification_data = created_report_model.model_dump()
            # Construct download URL (e.g., presigned S3 URL or link to API endpoint)
            # download_url = await get_presigned_s3_url(bucket_name, s3_key) # Placeholder
            download_url = (
                f"Access via API or path: {file_location_uri}"  # Simple placeholder
            )
            report_notification_data["download_url"] = download_url

            await alert_client.send_report_notification(
                report_data=report_notification_data
            )
        except Exception as e:
            logger.error(
                f"Failed to send report notification for report ID {created_report_model.id}: {e}"
            )

        finally:
            # Clean up local temporary file if it wasn't the final storage location
            if (
                file_location_uri
                and not file_location_uri.startswith("file://")
                and os.path.exists(local_pdf_path)
            ):
                try:
                    os.remove(local_pdf_path)
                    logger.debug(f"Removed temporary local PDF file: {local_pdf_path}")
                except OSError as e:
                    logger.error(
                        f"Error removing temporary PDF file {local_pdf_path}: {e}"
                    )

    generation_duration = (
        datetime.now(timezone.utc) - generation_start_time
    ).total_seconds()
    logger.info(f"PDF report generation finished in {generation_duration:.2f} seconds.")
