# Models (for serializing JSON)
# -----------------------------
import datetime
from typing import Optional

from pydantic import BaseModel


class TaskAdditional(BaseModel):
    force_termination: bool
    force_run: bool

    last_run: Optional[datetime.datetime]
    last_success: Optional[datetime.datetime]
    last_fail: Optional[datetime.datetime]
    last_terminate: Optional[datetime.datetime]
    last_inaction: Optional[datetime.datetime]
    last_crash: Optional[datetime.datetime]


class Task(BaseModel):
    name: str
    description: Optional[str]
    period: str

    status: str
    is_running: bool
    disabled: bool

    additional: TaskAdditional


class TaskStatus(BaseModel):
    name: str
    status: bool
