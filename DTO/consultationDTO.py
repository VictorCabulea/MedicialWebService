from pydantic import BaseModel


class ConsultationDTO(BaseModel):
    id_patient: int
    id_doctor: int
    date: str
    diagnostic: str
    investigations: str
