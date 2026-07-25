
"""
This file acts as the strict Data Contract for the entire machine learning pipeline. 
Instead of relying on loose dictionaries, this utilizes Pydantic to strictly enforce 
the "Suggested Synthetic Data Schema" required by the project brief. By validating 
every single log at the point of generation, we guarantee that the downstream ML model 
will never crash due to malformed data, missing fields, or incorrect data types.
"""


from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EntityType(str, Enum):
    USER = "user"
    SERVICE_ACCOUNT = "service_account"
    EDGE_DEVICE = "edge_device"

class LabelType(str, Enum):
    NORMAL = "normal"
    BRUTE_FORCE = "brute_force"
    IMPOSSIBLE_TRAVEL = "impossible_travel"
    CREDENTIAL_STUFFING = "credential_stuffing"
    LATERAL_MOVEMENT = "lateral_movement"
    DEVICE_SPOOFING = "device_spoofing"
    LOW_AND_SLOW = "low_and_slow"
    INSIDER_DRIFT = "insider_drift"   

# The core blueprint for a single access log
class AccessLog(BaseModel):
    entity_id: str = Field(..., description="user_id or device_id")
    entity_type: EntityType
    timestamp: datetime = Field(..., description="access or connection time")
    source_ip: str = Field(..., description="origin of the access")
    geo_location: str = Field(..., description="city, country, or coordinates")
    resource_accessed: str = Field(..., description="file, endpoint, port, or device function")
    auth_method: str = Field(..., description="password, token, certificate, biometric")
    session_duration: float = Field(..., description="length of connection in seconds")
    command_sequence: List[str] = Field(default_factory=list, description="ordered list of actions taken")
    device_fingerprint: str = Field(..., description="OS/firmware version, MAC address, protocol used")
    label: LabelType = Field(default=LabelType.NORMAL, description="hidden at inference, used for training")

# Execution block to test the schema locally
if __name__ == "__main__":
    # Create a dummy valid log to verify the schema works
    test_log = AccessLog(
        entity_id="usr_8923",
        entity_type=EntityType.USER,
        timestamp=datetime.now(),
        source_ip="192.168.1.45",
        geo_location="London, UK",
        resource_accessed="/api/v1/financial_records",
        auth_method="token",
        session_duration=125.5,
        command_sequence=["GET /dashboard", "POST /query"],
        device_fingerprint="macOS 13.4 | Safari 16.5",
        label=LabelType.NORMAL
    )
    
    print("Schema Validation Successful!")
    print(test_log.model_dump_json(indent=2))