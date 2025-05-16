from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import logger
from app.db import crud
from app.db.session import get_db
from app.schemas import AlertCreate, HoneypotData  # Use AlertCreate for DB entry
from app.services.alerting.client import alert_client
from app.services.enrichment.abuseipdb import get_abuseipdb_score

# Import enrichment and alerting services
from app.services.enrichment.geoip import get_geoip_data
from app.services.validation import validate_ip

router = APIRouter()


async def process_honeypot_data(db: AsyncSession, data: HoneypotData):
    """
    Background task to process honeypot data: enrich, store, alert.
    """
    logger.info(f"Processing honeypot data for IP: {data.source_ip}")
    ip_info = None
    abuse_score = None
    alert_payload = data.model_dump()  # Use the raw data as part of the alert payload

    # Validate IP address
    ip_str = str(data.source_ip)
    if not validate_ip(ip_str):
        logger.warning(f"Invalid IP address format: {ip_str}")
        return

    try:
        # 1. Enrich IP address (GeoIP, AbuseIPDB)
        ip_info = await get_geoip_data(ip_str)
        abuse_score = await get_abuseipdb_score(ip_str)
        logger.debug(
            f"Enrichment for {data.source_ip}: Geo={ip_info}, AbuseScore={abuse_score}"
        )

        # 2. Create Alert record in database
        alert_in = AlertCreate(
            alert_type="Honeypot Triggered",
            source_ip=data.source_ip,
            ip_info=ip_info,
            payload=alert_payload,  # Store the received data
            abuse_score=abuse_score,
            severity="medium",  # Or determine severity based on rules/score
            status="new",
            triggered_at=data.timestamp,  # Use timestamp from data if reliable
        )
        created_alert = await crud.alert.create(db=db, obj_in=alert_in)
        logger.info(
            f"Honeypot alert created in DB for IP {data.source_ip}, Alert ID: {created_alert.id}"
        )

        # 3. Trigger external alerts (Slack, Email, Discord)
        # Pass the enriched data and DB alert object to the alerting client
        await alert_client.send_alert(
            alert_data=created_alert
        )  # Pass the created alert object
        logger.info(
            f"External alert sent for honeypot trigger from IP {data.source_ip}"
        )

    except Exception as e:
        logger.error(
            f"Error processing honeypot data for IP {data.source_ip}: {e}",
            exc_info=True,
        )
        # Optionally, create a simpler alert indicating processing failure
        try:
            alert_in_error = AlertCreate(
                alert_type="Honeypot Processing Error",
                source_ip=data.source_ip,
                payload={"error": str(e), "original_data": alert_payload},
                severity="high",
                status="new",
                triggered_at=data.timestamp,
            )
            await crud.alert.create(db=db, obj_in=alert_in_error)
        except Exception as db_err:
            logger.error(
                f"CRITICAL: Failed to log honeypot processing error to DB: {db_err}"
            )


# Note: This endpoint should ideally be secured (e.g., IP whitelisting, secret header)
# if it's exposed externally, even though it receives data from internal systems like AWS WAF.
@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def receive_honeypot_trigger(
    # Use Request directly to potentially access headers for auth/verification
    request: Request,
    # Pydantic model for the expected body structure
    honeypot_data: HoneypotData,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Receives mirrored traffic data (e.g., from AWS WAF logs via Kinesis/Lambda).
    Validates input, triggers background task for enrichment, DB storage, and alerting.

    Security Note: Ensure this endpoint is properly secured if exposed.
    Consider checking a secret header or source IP expected from AWS services.
    """
    # --- Optional Security Check ---
    # Example: Check for a secret header
    # expected_secret = settings.HONEYPOT_SECRET_HEADER
    # received_secret = request.headers.get("X-TwinSecure-Honeypot-Secret")
    # if not expected_secret or not received_secret or received_secret != expected_secret:
    #     logger.warning(f"Unauthorized honeypot access attempt from {request.client.host}")
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or missing secret header")

    client_ip = request.client.host if request.client else "unknown"
    logger.info(
        f"Received honeypot trigger from client IP: {client_ip}, for source IP: {honeypot_data.source_ip}"
    )

    # Add processing to background tasks to respond quickly
    background_tasks.add_task(process_honeypot_data, db, honeypot_data)

    logger.debug("Honeypot data processing added to background task queue.")
    return {
        "message": "Honeypot data received and queued for processing.",
        "client_ip": client_ip,
    }
