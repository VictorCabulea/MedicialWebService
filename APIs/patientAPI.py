from fastapi import APIRouter, Response, HTTPException, status, Query

from DTO.validationDTO import *
from Databases.SQL.SQLDatabase import Patients
from DTO.patientDTO import *

router = APIRouter()


def create_response_data(patient: PatientDTO):
    response_data = {
        "patient": {
            "cnp": patient.cnp,
            "lastName": patient.lastName,
            "firstName": patient.firstName,
            "email": patient.email,
            "phoneNumber": patient.phoneNumber,
            "age": patient.age,
            "birthday": patient.birthday,
            "is_active": patient.is_active,
            "links": {
                "self": {
                    "href": f"/api/medicineProject/patients/{patient.cnp}", "type": "GET"
                },
                "update_cnp": {"href": f"/api/medicineProject/patients/{patient.cnp}/cnp", "type": "PUT"},
                "update_name": {"href": f"/api/medicineProject/patients/{patient.cnp}/name", "type": "PUT"},
                "update_email": {"href": f"/api/medicineProject/patients/{patient.cnp}/email",
                                 "type": "PUT"},
                "update_phone_number": {"href": f"/api/medicineProject/patients/{patient.cnp}/phone_number",
                                        "type": "PUT"},
                "update_age_and_birthday": {
                    "href": f"/api/medicineProject/patients/{patient.cnp}/age_and_birthday",
                    "type": "PUT"},
                "update_phone_is_active": {"href": f"/api/medicineProject/patients/{patient.cnp}/is_active",
                                           "type": "PUT"},
                "delete patient": {
                    "href": f"/api/medicineProject/patients/{patient.cnp}", "type": "DELETE"
                }
            }
        },
    }

    return response_data


@router.post("/api/medicineProject/patients/")
async def create_patient(
        patient: PatientDTO,
        response: Response,
):
    existing_patient_cnp = Patients.get_or_none(cnp=patient.cnp)
    existing_patient_email = Patients.get_or_none(email=patient.email)
    existing_patient_phone = Patients.get_or_none(phoneNumber=patient.phoneNumber)
    # cnp-ul, email-ul si numarul de telefon nu poate fi acelasi la mai multi pacienti
    if existing_patient_cnp or existing_patient_email or existing_patient_phone:
        raise HTTPException(status_code=status.HTTP_200_OK,
                            detail="A patient with this information already exists")

    if is_valid_patient(patient):
        new_patient = Patients.create(
            cnp=patient.cnp,
            lastName=patient.lastName,
            firstName=patient.firstName,
            email=patient.email,
            phoneNumber=patient.phoneNumber,
            age=patient.age,
            birthday=patient.birthday,
            is_active=True
        )

        response.status_code = status.HTTP_201_CREATED

        response_data = create_response_data(new_patient)
    else:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = {
            "message": f"The patient could not be registered due to errors in the input data!",
            "_links": {
                "view patients": {"href": "/api/medicineProject/patients", "type": "GET"},
                "add new patient": {"href": "/api/medicineProject/patients/create", "type": "POST"},
            }
        }

    return response_data


@router.get("/api/medicineProject/patients/{patient_cnp}")
async def get_patient(patient_cnp: str, response: Response):
    try:
        patient = Patients.get_by_cnp(patient_cnp)

        response.status_code = status.HTTP_200_OK

        response_data = create_response_data(patient)

        return response_data

    except Patients.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )


@router.get("/api/medicineProject/patients/")
async def get_patients(
    response: Response,
    cnp: str = Query(None, title="CNP", description="Personal Numeric Code of the patient."),
    last_name: str = Query(None, title="Last Name", description="Last name of the patient."),
    first_name: str = Query(None, title="First Name", description="First name of the patient."),
    phone_number: str = Query(None, title="Phone Number", description="Phone Number of the patient."),
    email: str = Query(None, title="Email", description="Email of the patient."),
):
    try:
        if cnp:
            if not is_valid_cnp(cnp):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            patients = Patients.filter(Patients.cnp == cnp)

        elif last_name and first_name:
            if not (is_valid_name(last_name) and is_valid_name(first_name)):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            patients = Patients.filter((Patients.lastName == last_name) & (Patients.firstName == first_name))

        elif phone_number:
            if not is_valid_phone_number(phone_number):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            patients = Patients.filter(Patients.phoneNumber == phone_number)

        elif email:
            if not is_valid_email(email):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            patients = Patients.filter(Patients.email == email)

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least the last_name and first_name, or CNP, or email, or phone number should be provided.",
            )

        if patients.count() == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No patients found with the given criteria.",
            )
        else:
            response.status_code = status.HTTP_200_OK

            patients_data = [create_response_data(patient) for patient in patients]
            response_data = {"patients": patients_data}

            return response_data

    except Patients.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No patients found with the given criteria.",
        )



@router.put("/api/medicineProject/patients/{patient_cnp}/name")
async def update_patient_name(
        patient_cnp: str,
        updated_lastName: str,
        updated_firstName: str,
        response: Response,
):
    try:
        if is_valid_name(updated_lastName) and is_valid_name(updated_firstName):
            patient = Patients.get_by_cnp(patient_cnp)

            patient.lastName = updated_lastName
            patient.firstName = updated_firstName

            patient.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Validation error in input data")

    except Patients.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")


@router.put("/api/medicineProject/patients/{patient_cnp}/email")
async def update_patient_email(
        patient_cnp: str,
        updated_email: str,
        response: Response,
):
    try:
        patient = Patients.get_by_cnp(patient_cnp)
        conflicting_email_patient = Patients.get_by_email(updated_email)
        if conflicting_email_patient:
            raise HTTPException(status_code=status.HTTP_200_OK,
                                detail="Another patient already has this email")
        # nu pot fi mai multi pacienti cu acelasi email
        if is_valid_email(updated_email):
            print(patient.email)
            print()
            patient.email = updated_email

            patient.save()
            print(patient.email)
            print()
            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Validation error in input data")

    except Patients.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")


@router.put("/api/medicineProject/patients/{patient_cnp}/phone_number")
async def update_patient_phone_number(
        patient_cnp: str,
        updated_phoneNumber: str,
        response: Response,
):
    try:
        patient = Patients.get_by_cnp(patient_cnp)

        conflicting_phone_patient = Patients.get_by_phone_number(updated_phoneNumber)
        # nu pot fi mai multi pacienti cu acelasi numar de telefon
        if conflicting_phone_patient:
            raise HTTPException(status_code=status.HTTP_200_OK,
                                detail="Another patient already has this phone number")

        if is_valid_phone_number(updated_phoneNumber):
            patient.phone_number = updated_phoneNumber

            patient.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Validation error in input data")

    except Patients.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")


@router.put("/api/medicineProject/patients/{patient_cnp}/age_and_birthday")
async def update_patient_age_and_birthday(
        patient_cnp: str,
        updated_age: int,
        updated_birthday: str,
        response: Response,
):
    try:
        patient = Patients.get_by_cnp(patient_cnp)

        if is_valid_age(updated_age) and is_valid_date(updated_birthday):
            patient.age = updated_age
            patient.birthday = updated_birthday

            patient.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Validation error in input data")

    except Patients.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")


@router.put("/api/medicineProject/patients/{patient_cnp}/is_active")
async def update_patient_is_active(
        patient_cnp: str,
        updated_is_active: bool,
        response: Response,
):
    try:
        if is_valid_is_active(updated_is_active):
            patient = Patients.get_by_cnp(patient_cnp)

            patient.is_active = updated_is_active

            patient.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Validation error in input data")

    except Patients.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")


@router.delete("/api/medicineProject/patients/{patient_id}")
async def delete_patient(patient_cnp: str, response: Response):
    try:
        patient = Patients.get_by_cnp(patient_cnp)

        patient.delete_instance()

        response.status_code = status.HTTP_204_NO_CONTENT

    except Patients.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )
