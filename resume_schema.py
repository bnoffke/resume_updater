from pydantic import BaseModel
from typing import Dict, List, Optional

class Personal(BaseModel):
    name: str
    location: str
    email: Optional[str] = None
    phone: Optional[str] = None

class Job(BaseModel):
    title: str
    location: str
    time_range: str
    skills: List[str]
    summary: str

class Resume(BaseModel):
    personal: Personal
    jobs: Dict[str, Job]
