from datetime import datetime
from dataclasses import dataclass
from typing import Optional, Dict, Any

from pydantic import BaseModel


@dataclass
class UserEntity:
    id: int
    telegram_id: str
    goal: Optional[str] = None


@dataclass
class GoalEntity:
    id: int
    user_id: int
    goal_description: str
    created_at: datetime


@dataclass
class NutritionAnswer:

    text: str
    is_function_call: bool = False
    function_name: Optional[str] = None
    function_args: Optional[Dict[str, Any]] = None


@dataclass
class PhotoAnalysisResult:
    text: str


class GoalDetectionResponse(BaseModel):

    text: Optional[str] = None
    is_function_call: bool = False
    function_name: Optional[str] = None
    function_args: Optional[Dict[str, Any]] = None
