"""
TwinSecure - Advanced Cybersecurity Platform

Copyright © 2024 TwinSecure. All rights reserved.

Honeypot data schemas for WAF traffic mirroring.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress


class HoneypotData(BaseModel):
    """
    Schema for data received at the /honeypot endpoint.
    
    Reflects AWS WAF log structure with field aliases for camelCase.
    """
    
    timestamp: str  # Or datetime, depending on source format
    source_ip: IPvAnyAddress = Field(..., alias="sourceIp")
    request_id: str | None = Field(None, alias="requestId")
    http_method: str | None = Field(None, alias="httpMethod")
    uri: str | None = None
    headers: dict[str, Any] | None = None
    query_string: str | None = Field(None, alias="queryString")
    body: str | None = None  # Raw body, might need parsing
    waf_action: str | None = Field(None, alias="action")  # ALLOW, BLOCK
    rule_group_list: list | None = Field(None, alias="ruleGroupList")
    
    model_config = ConfigDict(
        populate_by_name=True,  # Allows using aliases
        extra="ignore"  # Ignore extra fields from WAF logs
    )
