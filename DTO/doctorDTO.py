from pydantic import BaseModel


class DoctorDTO(BaseModel):
    last_name: str
    first_name: str
    email: str
    phone_number: str
    speciality: str
