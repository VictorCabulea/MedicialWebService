from pydantic import BaseModel


class DoctorDTO(BaseModel):
    name: str
    processing_time: int
    result: str
