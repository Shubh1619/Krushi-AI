from pydantic import BaseModel
from typing import List, Optional


class Scheme(BaseModel):
    name: str
    type: str
    description: str
    eligibility: str
    how_to_apply: str
    application_portal: str


class GeminiSchemeResponse(BaseModel):
    schemes: List[Scheme]
