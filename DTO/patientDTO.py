from pydantic import BaseModel


class PatientDTO(BaseModel):
    cnp: str
    lastName: str
    firstName: str
    email: str
    phoneNumber: str
    age: int
    birthday: str
    is_active: bool
