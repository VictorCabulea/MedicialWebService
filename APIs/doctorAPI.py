from fastapi import APIRouter, Response, HTTPException, status, Query
from starlette.responses import JSONResponse

from DTO.validationDTO import *
from Databases.SQL.SQLDatabase import Doctors
from DTO.doctorDTO import *

router = APIRouter()


def create_response_data(doctor: DoctorDTO):
    response_data = {
        "doctor": {
            "id": doctor.id,
            "last_name": doctor.last_name,
            "first_name": doctor.first_name,
            "email": doctor.email,
            "phone_number": doctor.phone_number,
            "speciality": doctor.speciality,
            "links": {
                "self": {
                    "href": f"/api/medicineProject/doctors/{doctor.id}", "type": "GET"
                },
                "update_name": {"href": f"/api/medicineProject/doctors/{doctor.id}/name", "type": "PUT"},
                "update_email": {"href": f"/api/medicineProject/doctors/{doctor.id}/email", "type": "PUT"},
                "update_phone_number": {"href": f"/api/medicineProject/doctors/{doctor.id}/phone_number",
                                        "type": "PUT"},
                "update_speciality": {"href": f"/api/medicineProject/doctors/{doctor.id}/speciality",
                                      "type": "PUT"},
                "delete doctor": {
                    "href": f"/api/medicineProject/doctors/{doctor.id}", "type": "DELETE"
                }
            }
        },
    }

    return response_data


@router.post("/api/medicineProject/doctors")
async def create_doctor(
        doctor: DoctorDTO,
        response: Response,
):
    existing_doctor_email = Doctors.get_or_none(email=doctor.email)
    existing_doctor_phone = Doctors.get_or_none(phone_number=doctor.phone_number)

    if existing_doctor_email or existing_doctor_phone:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="A doctor with this information already exists")

    if is_valid_doctor(doctor):
        new_doctor = Doctors.create(
            last_name=doctor.last_name,
            first_name=doctor.first_name,
            email=doctor.email,
            phone_number=doctor.phone_number,
            speciality=doctor.speciality
        )

        response.status_code = status.HTTP_201_CREATED
        response_data = create_response_data(new_doctor)

    else:
        response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        response_data = {
            "message": f"The doctors could not be registered due to errors in the input data!",
            "_links": {
                "view doctors": {"href": "/api/medicineProject/doctors", "type": "GET"},
                "add new doctor": {"href": "/api/medicineProject/doctors/create", "type": "POST"},
            }
        }

    return response_data


@router.get("/api/medicineProject/doctors/{doctor_id}")
async def get_doctor_by_id(doctor_id: int, response: Response):
    try:
        doctor = Doctors.get_by_id(doctor_id)

        response.status_code = status.HTTP_200_OK

        response_data = create_response_data(doctor)

        return response_data
    except Doctors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )


@router.get("/api/medicineProject/doctors/")
async def get_doctors(
        response: Response,
        last_name: str = Query(None, title="Last Name", description="Last name of the doctor."),
        first_name: str = Query(None, title="First Name", description="First name of the doctor."),
        speciality: str = Query(None, title="Speciality", description="Speciality of the doctor."),
        email: str = Query(None, title="Email", description="Email of the doctor."),
        phone_number: str = Query(None, title="Phone Number", description="Phone number of the doctor."),
):
    try:
        if last_name and first_name:
            if not (is_valid_name(last_name) and is_valid_name(first_name)):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            doctors = Doctors.filter((Doctors.last_name == last_name) & (Doctors.first_name == first_name))

        elif speciality:
            if not is_valid_speciality(speciality):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            doctors = Doctors.filter(Doctors.speciality == speciality)

        elif email:
            if not is_valid_email(email):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            doctor = Doctors.get_by_email(email)
            response_data = create_response_data(doctor)
            return [response_data] if response_data else []

        elif phone_number:
            if not is_valid_phone_number(phone_number):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Validation error in input data",
                )

            doctor = Doctors.get_by_phone_number(phone_number)
            response_data = create_response_data(doctor)
            return [response_data] if response_data else []

        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one of last_name, first_name, speciality, email, or phone_number should be provided.",
            )

        if not doctors:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No doctors found with the given criteria.",
            )

        response.status_code = status.HTTP_200_OK
        response_data = [create_response_data(doctor) for doctor in doctors]
        return response_data

    except Doctors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No doctors found with the given criteria.",
        )


@router.put("/api/medicineProject/doctors/{doctor_id}/name")
async def update_doctor_name(
        doctor_id: int,
        updated_lastName: str,
        updated_firstName: str,
        response: Response,
):
    # nu am adaugat verificare de unicitate a numelui si prenumelui pentru ca exissta cazuri in care doua persoane au
    # acelasi nume
    try:
        if is_valid_name(updated_lastName) and is_valid_name(updated_firstName):
            doctor = Doctors.get_by_id(doctor_id)

            doctor.last_name = updated_lastName
            doctor.first_name = updated_firstName

            doctor.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Validation error in input data",
            )

    except Doctors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )


@router.put("/api/medicineProject/doctors/email/{email}")
async def update_doctor_email(
        email: str,
        updated_email: str,
        response: Response,
):
    try:
        if is_valid_email(updated_email):
            doctor = Doctors.get_by_email(email)
            print(doctor)
            # am presupus ca nu pot fi mai multi doctori cu aceeasi adresa de email
            conflicting_email_doctor = Doctors.get_or_none(email=updated_email)

            if conflicting_email_doctor:
                raise HTTPException(status_code=status.HTTP_200_OK,
                                    detail="Another doctor already has this email")
            else:
                doctor.email = updated_email

                doctor.save()

                response.status_code = status.HTTP_204_NO_CONTENT
                return None
        else:
            return JSONResponse(content="Validation error in input data",
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    except Doctors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )


@router.put("/api/medicineProject/doctors/{doctor_id}/phone_number")
async def update_doctor_phone_number(
        doctor_id: int,
        updated_phone_number: str,
        response: Response,
):
    try:
        if is_valid_phone_number(updated_phone_number):
            doctor = Doctors.get_by_id(doctor_id)

            # am presupus ca nu pot fi mai multi doctori cu acelasi numar de telefon
            conflicting_phone_doctor = Doctors.get_or_none(phoneNumber=updated_phone_number)

            if conflicting_phone_doctor and conflicting_phone_doctor.id != doctor_id:
                raise HTTPException(status_code=status.HTTP_200_OK,
                                    detail="Another doctor already has this phone number")

            doctor.phone_number = updated_phone_number

            doctor.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            return JSONResponse(content="Validation error in input data",
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    except Doctors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )


@router.put("/api/medicineProject/doctors/{doctor_id}/speciality")
async def update_doctor_speciality(
        doctor_id: int,
        updated_speciality: str,
        response: Response,
):
    try:
        if is_valid_speciality(updated_speciality):
            doctor = Doctors.get_by_id(doctor_id)

            doctor.speciality = updated_speciality

            doctor.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return None
        else:
            return JSONResponse(content="Validation error in input data",
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

    except Doctors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )


@router.delete("/api/medicineProject/doctors/{doctor_id}")
async def delete_doctor(doctor_id: int, response: Response):
    try:
        doctor = Doctors.get_by_id(doctor_id)

        doctor.delete_instance()

        response.status_code = status.HTTP_204_NO_CONTENT

    except Doctors.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor not found",
        )
