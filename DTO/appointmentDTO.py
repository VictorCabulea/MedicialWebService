from pydantic import BaseModel


class AppointmentDTO(BaseModel):
    id_patient: int
    id_doctor: int
    date: str
    status: str
