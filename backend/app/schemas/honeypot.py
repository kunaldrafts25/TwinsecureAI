from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional, Dict, Any

class HoneypotData(BaseModel):
    """
    Schema for data received at the /honeypot endpoint.
    This should reflect the structure of the mirrored traffic data (e.g., from AWS WAF logs).
    Adjust fields based on the actual data format you receive.
    """
    timestamp: str # Or datetime, depending on source format
    source_ip: IPvAnyAddress = Field(..., alias="sourceIp") # Example: alias if source uses camelCase
    request_id: Optional[str] = Field(None, alias="requestId")
    http_method: Optional[str] = Field(None, alias="httpMethod")
    uri: Optional[str] = None
    headers: Optional[Dict[str, Any]] = None
    query_string: Optional[str] = Field(None, alias="queryString")
    body: Optional[str] = None # Raw body, might need parsing
    waf_action: Optional[str] = Field(None, alias="action") # e.g., ALLOW, BLOCK
    rule_group_list: Optional[list] = Field(None, alias="ruleGroupList") # Rules triggered

    class Config:
        allow_population_by_field_name = True # Allows using aliases like sourceIp
        # Consider adding extra='ignore' if the incoming data might have extra fields
        # extra = 'ignore'
