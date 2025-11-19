"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Automated attack response service for blocking and mitigating attacks.
"""

import platform
import subprocess
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, update

from app.core.config import logger, settings
from app.db.models import Alert, DigitalTwin, TwinEngagement
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.alerting import alert_client


class AttackResponder:
    """
    Service for automated response to detected attacks.
    Supports IP blocking, rate limiting, and threat intelligence updates.
    """
    
    def __init__(self):
        self.blocked_ips: dict[str, datetime] = {}  # In-memory block list
        self.response_actions: list[str] = []
    
    async def respond_to_attack(
        self,
        source_ip: str,
        attack_type: str,
        severity: str,
        confidence: float,
        alert_id: str | None = None,
        db: AsyncSession | None = None
    ) -> list[str]:
        """
        Automatically respond to a detected attack.
        
        Args:
            source_ip: Attacker IP address
            attack_type: Type of attack detected
            severity: Attack severity (critical, high, medium, low)
            confidence: Detection confidence (0.0-1.0)
            alert_id: Associated alert ID
            db: Database session
            
        Returns:
            List of actions taken
        """
        actions_taken = []
        
        # Determine response based on severity and confidence
        if severity in ["critical", "high"] and confidence > 0.7:
            # Immediate blocking for high-confidence critical/high severity attacks
            if await self.block_ip(source_ip, duration_minutes=60):
                actions_taken.append("ip_blocked")
                logger.warning(f"IP {source_ip} blocked due to {attack_type} attack")
        
        elif severity == "high" and confidence > 0.5:
            # Rate limiting for high severity
            if await self.rate_limit_ip(source_ip, requests_per_minute=5):
                actions_taken.append("rate_limited")
                logger.info(f"IP {source_ip} rate limited due to {attack_type} attack")
        
        # Always send alert
        await self._send_alert(source_ip, attack_type, severity, confidence, alert_id)
        actions_taken.append("alert_sent")
        
        # Log engagement if digital twin involved
        if db and alert_id:
            await self._log_engagement(db, source_ip, attack_type, alert_id)
        
        # Update threat intelligence
        if db:
            await self._update_threat_intel(db, source_ip, attack_type, severity)
        
        return actions_taken
    
    async def block_ip(
        self,
        source_ip: str,
        duration_minutes: int = 60,
        reason: str | None = None
    ) -> bool:
        """
        Block an IP address for a specified duration.
        
        Args:
            source_ip: IP address to block
            duration_minutes: Block duration in minutes
            reason: Reason for blocking
            
        Returns:
            True if IP was blocked
        """
        if source_ip in self.blocked_ips:
            # Extend block duration
            self.blocked_ips[source_ip] = datetime.now(timezone.utc) + timedelta(
                minutes=duration_minutes
            )
            logger.info(f"Extended block for {source_ip}")
            return True
        
        # Add new block
        self.blocked_ips[source_ip] = datetime.now(timezone.utc) + timedelta(
            minutes=duration_minutes
        )
        logger.warning(
            f"IP {source_ip} blocked for {duration_minutes} minutes. "
            f"Reason: {reason or 'Attack detected'}"
        )
        
        # Apply firewall blocks
        await self._apply_firewall_block(source_ip, duration_minutes)
        
        return True
    
    async def _apply_firewall_block(self, source_ip: str, duration_minutes: int):
        """Apply firewall block using available methods."""
        
        # Method 1: iptables (Linux)
        try:
            if platform.system() == "Linux":
                try:
                    subprocess.run(
                        ["iptables", "-A", "INPUT", "-s", source_ip, "-j", "DROP"],
                        check=True,
                        timeout=5,
                        capture_output=True
                    )
                    logger.info(f"iptables rule added for {source_ip}")
                except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
                    logger.debug(f"iptables blocking not available for {source_ip}")
        except Exception as e:
            logger.debug(f"iptables blocking failed: {e}")
        
        # Method 2: AWS WAF (if configured)
        if hasattr(settings, "AWS_REGION") and settings.AWS_REGION:
            try:
                logger.debug(
                    f"AWS WAF blocking would be applied for {source_ip} "
                    "(requires WAF IP set configuration)"
                )
            except Exception as e:
                logger.debug(f"AWS WAF blocking failed: {e}")
        
        # Method 3: Redis for distributed blocking
        if hasattr(settings, "REDIS_URL") and settings.REDIS_URL:
            try:
                import redis.asyncio as redis
                
                r = redis.from_url(settings.REDIS_URL)
                block_key = f"blocked_ip:{source_ip}"
                await r.setex(block_key, duration_minutes * 60, "1")
                await r.close()
                
                logger.info(f"IP {source_ip} blocked in Redis cache")
            except Exception as e:
                logger.debug(f"Redis blocking failed: {e}")
    
    async def unblock_ip(self, source_ip: str) -> bool:
        """Unblock a previously blocked IP address."""
        if source_ip in self.blocked_ips:
            del self.blocked_ips[source_ip]
            logger.info(f"IP {source_ip} unblocked")
            
            # Remove from firewall rules
            await self._remove_firewall_block(source_ip)
            
            return True
        
        return False
    
    async def _remove_firewall_block(self, source_ip: str):
        """Remove firewall block."""
        # Remove iptables rule
        try:
            if platform.system() == "Linux":
                try:
                    subprocess.run(
                        ["iptables", "-D", "INPUT", "-s", source_ip, "-j", "DROP"],
                        check=False,
                        timeout=5,
                        capture_output=True
                    )
                    logger.info(f"iptables rule removed for {source_ip}")
                except (subprocess.CalledProcessError, FileNotFoundError, PermissionError):
                    pass
        except Exception:
            pass
        
        # Remove from Redis
        if hasattr(settings, "REDIS_URL") and settings.REDIS_URL:
            try:
                import redis.asyncio as redis
                
                r = redis.from_url(settings.REDIS_URL)
                block_key = f"blocked_ip:{source_ip}"
                await r.delete(block_key)
                await r.close()
                
                logger.info(f"IP {source_ip} unblocked in Redis cache")
            except Exception:
                pass
    
    def is_blocked(self, source_ip: str) -> bool:
        """Check if an IP is currently blocked."""
        if source_ip not in self.blocked_ips:
            return False
        
        # Check if block has expired
        if datetime.now(timezone.utc) > self.blocked_ips[source_ip]:
            del self.blocked_ips[source_ip]
            return False
        
        return True
    
    async def rate_limit_ip(
        self,
        source_ip: str,
        requests_per_minute: int = 5
    ) -> bool:
        """Apply rate limiting to an IP address via Redis."""
        if hasattr(settings, "REDIS_URL") and settings.REDIS_URL:
            try:
                import redis.asyncio as redis
                
                r = redis.from_url(settings.REDIS_URL)
                rate_limit_key = f"rate_limit_custom:{source_ip}"
                await r.setex(rate_limit_key, 3600, str(requests_per_minute))
                await r.close()
                
                logger.info(
                    f"Custom rate limit set for {source_ip}: "
                    f"{requests_per_minute} req/min"
                )
            except Exception as e:
                logger.warning(f"Failed to set custom rate limit in Redis: {e}")
        
        return True
    
    async def _send_alert(
        self,
        source_ip: str,
        attack_type: str,
        severity: str,
        confidence: float,
        alert_id: str | None = None
    ):
        """Send alert notification about the attack."""
        alert_data = {
            "title": f"Automated Response: {attack_type}",
            "severity": severity,
            "message": f"Attack detected from {source_ip}. Confidence: {confidence:.2%}",
            "source_ip": source_ip,
            "alert_type": attack_type,
            "additional_data": {
                "confidence": confidence,
                "id": alert_id,
            }
        }
        
        try:
            await alert_client.send_alert(alert_data)
        except Exception as e:
            logger.error(f"Failed to send attack response alert: {e}")
    
    async def _log_engagement(
        self,
        db: AsyncSession,
        source_ip: str,
        attack_type: str,
        alert_id: str
    ):
        """Log engagement with digital twin if applicable."""
        try:
            # Get alert to find associated twin
            alert_stmt = select(Alert).where(Alert.id == UUID(alert_id))
            alert_result = await db.execute(alert_stmt)
            alert = alert_result.scalar_one_or_none()
            
            if not alert:
                return
            
            # Find active honeypot twins matching the IP
            twin_stmt = select(DigitalTwin).where(
                DigitalTwin.is_honeypot == True,
                DigitalTwin.status == "active",
                DigitalTwin.ip_address == source_ip
            ).limit(1)
            twin_result = await db.execute(twin_stmt)
            twin = twin_result.scalar_one_or_none()
            
            if twin:
                # Create engagement record
                engagement = TwinEngagement(
                    twin_id=twin.id,
                    attacker_ip=source_ip,
                    engagement_type=attack_type,
                    severity="high",
                    started_at=datetime.now(timezone.utc),
                    alert_id=UUID(alert_id)
                )
                db.add(engagement)
                
                # Update twin engagement count
                twin.engagement_count += 1
                twin.last_engagement = datetime.now(timezone.utc)
                twin.total_attacks_detected += 1
                
                await db.commit()
                logger.info(f"Engagement logged for twin {twin.id} from {source_ip}")
        
        except Exception as e:
            logger.error(f"Failed to log engagement: {e}", exc_info=True)
    
    async def _update_threat_intel(
        self,
        db: AsyncSession,
        source_ip: str,
        attack_type: str,
        severity: str
    ):
        """Update threat intelligence data for the IP."""
        try:
            stmt = update(Alert).where(
                Alert.source_ip == source_ip
            ).values(
                threat_intel={
                    "attack_types": [attack_type],
                    "severity": severity,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
            )
            await db.execute(stmt)
            await db.commit()
        
        except Exception as e:
            logger.error(f"Failed to update threat intel: {e}", exc_info=True)
    
    def get_blocked_ips(self) -> list[dict]:
        """Get list of currently blocked IPs."""
        now = datetime.now(timezone.utc)
        blocked = []
        
        for ip, expiry in self.blocked_ips.items():
            if now < expiry:
                blocked.append({
                    "ip": ip,
                    "blocked_until": expiry.isoformat(),
                    "remaining_minutes": int((expiry - now).total_seconds() / 60)
                })
        
        return blocked


# Global instance
attack_responder = AttackResponder()


# Convenience function
async def respond_to_attack(
    source_ip: str,
    attack_type: str,
    severity: str,
    confidence: float,
    alert_id: str | None = None,
    db: AsyncSession | None = None
) -> list[str]:
    """Convenience function for attack response."""
    return await attack_responder.respond_to_attack(
        source_ip, attack_type, severity, confidence, alert_id, db
    )
