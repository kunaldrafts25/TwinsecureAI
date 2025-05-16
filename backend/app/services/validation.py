import ipaddress
import re
from datetime import datetime
from typing import Any, Dict, Optional


def validate_alert_payload(data: Dict[str, Any]) -> bool:
    """
    Validate alert payload data.

    Args:
        data: Alert data to validate

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["type", "severity", "message"]
    if not all(field in data for field in required_fields):
        return False

    # Validate alert type
    valid_types = ["security", "performance", "system", "custom"]
    if data["type"] not in valid_types:
        return False

    # Validate severity
    valid_severities = ["critical", "error", "warning", "info"]
    if data["severity"] not in valid_severities:
        return False

    # Validate message
    if not isinstance(data["message"], str) or len(data["message"]) > 1000:
        return False

    # Validate payload if present
    if "payload" in data and data["payload"] is not None:
        if not isinstance(data["payload"], dict):
            return False
        if len(str(data["payload"])) > 10000:  # Limit payload size
            return False

    return True


def validate_report_payload(data: Dict[str, Any]) -> bool:
    """
    Validate report payload data.

    Args:
        data: Report data to validate

    Returns:
        bool: True if valid, False otherwise
    """
    required_fields = ["type", "status"]
    if not all(field in data for field in required_fields):
        return False

    # Validate report type
    valid_types = ["security", "performance", "audit", "custom"]
    if data["type"] not in valid_types:
        return False

    # Validate status
    valid_statuses = ["pending", "processing", "completed", "failed"]
    if data["status"] not in valid_statuses:
        return False

    # Validate download_url if present
    if "download_url" in data and data["download_url"] is not None:
        if not isinstance(data["download_url"], str):
            return False
        if not re.match(r"^https?://", data["download_url"]):
            return False

    return True


# This function is replaced by a more comprehensive version below


def validate_password(password: str) -> bool:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False
    return True


def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format.

    Args:
        date_str: Date string to validate
        format: Expected date format

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def validate_url(url: str) -> bool:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r"^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"
    return bool(re.match(pattern, url))


def validate_ip_address(ip: str) -> bool:
    """
    Validate IP address format.

    Args:
        ip: IP address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False

    # Check each octet
    return all(0 <= int(octet) <= 255 for octet in ip.split("."))


def validate_ip(ip: str) -> bool:
    """
    Validate IP address format.

    Args:
        ip: IP address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Validate IPv4 or IPv6 address
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False

    # Email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_hostname(hostname: str) -> bool:
    """
    Validate hostname format.

    Args:
        hostname: Hostname to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not hostname or len(hostname) > 255:
        return False

    # Hostname regex pattern
    pattern = r"^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(\.([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]))*$"
    return bool(re.match(pattern, hostname))


def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """
    Validate data against a JSON schema.

    Args:
        data: Data to validate
        schema: JSON schema to validate against

    Returns:
        bool: True if valid, False otherwise
    """

    def validate_type(value: Any, expected_type: str) -> bool:
        if expected_type == "string":
            return isinstance(value, str)
        elif expected_type == "number":
            return isinstance(value, (int, float))
        elif expected_type == "boolean":
            return isinstance(value, bool)
        elif expected_type == "object":
            return isinstance(value, dict)
        elif expected_type == "array":
            return isinstance(value, list)
        return False

    def validate_required(obj: Dict[str, Any], required: list) -> bool:
        return all(field in obj for field in required)

    def validate_properties(obj: Dict[str, Any], properties: Dict[str, Any]) -> bool:
        for key, value in obj.items():
            if key in properties:
                if not validate_type(value, properties[key]["type"]):
                    return False
        return True

    if "required" in schema and not validate_required(data, schema["required"]):
        return False

    if "properties" in schema and not validate_properties(data, schema["properties"]):
        return False

    return True
