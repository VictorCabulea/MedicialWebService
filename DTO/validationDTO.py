import re
from datetime import datetime

from DTO.appointmentDTO import AppointmentDTO
from DTO.consultationDTO import ConsultationDTO
from DTO.doctorDTO import DoctorDTO
from DTO.patientDTO import PatientDTO
from DTO.accountDTO import AccountDTO


diagnostics = ["Alzheimer", "Astigmatism", "Cataracta", "Cistita", "Diabet", "Enterocolita", "Entorsa", "Epilepsie",
             "Fractura", "Gripa", "Hepatita", "Hipermetropie", "Indigestie", "Luxatie", "Miocardita", "Miopie",
             "Parkinson", "Pericardita", "Raceala"]


def is_valid_name(name: str):
    return len(name) >= 3 and name[0].isupper()


def is_valid_email(email: str):
    email_pattern = re.compile(r'^[\w\.-]+@[a-zA-Z\d\.-]+\.[a-zA-Z]{2,}$')

    if email_pattern.match(email):
        return True
    return False


def is_valid_phone_number(phoneNumber: str):
    if len(phoneNumber) != 10 or not phoneNumber.startswith("07"):
        return False
    return True


def is_valid_speciality(speciality: str):
    if speciality in ["Chirurg", "Ortoped", "Pediatru", "Oftalmolog", "Cardiolog", "Neurolog"]:
        return True
    return False


def is_valid_cnp(cnp: str):
    if len(cnp) != 13:
        return False
    else:
        return True


def is_valid_age(age: int):
    if age < 0 or age > 120:
        return False
    return True


def is_valid_date(date: str):
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d")

        if parsed_date.year < 1903 or parsed_date.year > 2024:
            return False
        return True

    except ValueError:
        return False


def is_valid_is_active(is_active: bool):
    if is_active is True or is_active is False:
        return True
    return False


def is_valid_patient(patient: PatientDTO):
    if (
        not is_valid_cnp(patient.cnp) or
        not is_valid_name(patient.lastName) or
        not is_valid_name(patient.firstName) or
        not is_valid_email(patient.email) or
        not is_valid_phone_number(patient.phoneNumber) or
        not is_valid_age(patient.age) or
        not is_valid_date(patient.birthday) or
        not is_valid_is_active(patient.is_active)
    ):
        return False
    return True


def is_valid_doctor(doctor: DoctorDTO):
    if (
        not is_valid_name(doctor.last_name) or
        not is_valid_name(doctor.first_name) or
        not is_valid_email(doctor.email) or
        not is_valid_phone_number(doctor.phone_number) or
        not is_valid_speciality(doctor.speciality)
    ):
        return False
    return True


def is_valid_status(status: str):
    if status in ["Onorata", "Neprezentat", "Anulata"]:
        return True
    return False


def is_valid_appointment(appointment: AppointmentDTO):
    if (
        not is_valid_date(appointment.date) or
        not is_valid_status(appointment.status)
    ):
        return False
    return True


def is_valid_diagnostic(diagnostic: str):
    if diagnostic in diagnostics:
        return True
    return False


def is_valid_consultation(consultation: ConsultationDTO):
    if (
        not is_valid_date(consultation.date) or
        not is_valid_diagnostic(consultation.diagnostic)
    ):
        return False
    return True


def is_valid_user_name(user_name: str):
    return len(user_name) >= 5


def is_valid_password(password: str):
    if len(password) < 8:
        return False

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False

    return True


def is_valid_account(account: AccountDTO):
    if (
        not is_valid_name(account.last_name) or
        not is_valid_name(account.first_name) or
        not is_valid_user_name(account.user_name) or
        not is_valid_email(account.user_email) or
        not is_valid_password(account.password)
    ):
        return False
    return True
