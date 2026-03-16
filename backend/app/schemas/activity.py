from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel

class ActivityLogBase(BaseModel):
    type: str
    title: str
    subtitle: Optional[str] = None
    status: Optional[str] = None
    meta: Optional[Dict[str, Any]] = {}

class ActivityLogCreate(ActivityLogBase):
    pass

class ActivityLog(ActivityLogBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True
