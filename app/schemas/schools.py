from pydantic import BaseModel


class SchoolCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    contact_email: str
    contact_phone: str
