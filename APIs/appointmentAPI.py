from fastapi import APIRouter, Response, HTTPException, status, Header
from starlette.responses import JSONResponse

from DTO.validationDTO import *
from Databases.SQL.SQLDatabase import Appointments, Patients, Doctors

router = APIRouter()


def create_response_data(appointment: AppointmentDTO):
    response_data = {
        "appointment": {
            "id": appointment.id,
            "id_patient": appointment.id_patient,
            "id_doctor": appointment.id_doctor,
            "date": appointment.date,
            "status": appointment.status,
            "links": {
                "self": {
                    "href": f"/api/medicineProject/appointment/{appointment.id}", "type": "GET"
                },
                "update_id_patient": {
                    "href": f"/api/medicineProject/appointment/{appointment.id}/id_patient", "type": "PUT"
                },
                "update_id_doctor": {
                    "href": f"/api/medicineProject/appointment/{appointment.id}/id_doctor", "type": "PUT"
                },
                "update_date": {
                    "href": f"/api/medicineProject/appointment/{appointment.id}/date", "type": "PUT"
                },
                "update_status": {
                    "href": f"/api/medicineProject/appointment/{appointment.id}/id_patient", "type": "PUT"
                },
                "delete appointment": {
                    "href": f"/api/medicineProject/appointment/{appointment.id}", "type": "DELETE"
                }
            }
        },
    }

    return response_data


@router.post("/api/medicineProject/appointments/")
async def create_appointment(
        appointment: AppointmentDTO,
        response: Response,
):
    if is_valid_appointment(appointment):
        patient = Patients.get_or_none(cnp=appointment.id_patient)
        doctor = Doctors.get_or_none(id=appointment.id_doctor)

        if patient is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid patient ID",
            )
        elif doctor is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid doctor ID",
            )
        else:
            new_appointment = Appointments.create(
                id_patient=patient,
                id_doctor=doctor,
                date=appointment.date,
                status=appointment.status,
            )

            response.status_code = status.HTTP_201_CREATED

            response_data = create_response_data(new_appointment)
    else:
        response.status_code = status.HTTP_200_OK
        response_data = {
            "message": f"The appointment could not be registered due to errors in the input data!",
            "_links": {
                "view appointments": {
                    "href": "/api/medicineProject/appointment", "type": "GET",
                },
                "add new appointment": {
                    "href": "/api/medicineProject/appointment/create", "type": "POST",
                },
            }
        }

    return response_data


@router.get("/api/medicineProject/appointments/{appointment_id}")
async def get_appointment(appointment_id: int, response: Response):
    try:
        appointment = Appointments.get_by_id(appointment_id)

        response.status_code = status.HTTP_200_OK

        response_data = create_response_data(appointment)

        return response_data
    except Appointments.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


@router.get("/api/medicineProject/appointments/")
async def get_all_appointments(response: Response):
    appointments = Appointments.select()

    if appointments.count() == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No appointments found",
        )
    else:
        response.status_code = status.HTTP_200_OK

        appointments_data = [create_response_data(appointment) for appointment in appointments]
        response_data = {"doctors": appointments_data}

        return response_data


@router.put("/api/medicineProject/appointments/{appointment_id}/id_patient")
async def update_appointment_id_patient(
        appointment_id: int,
        updated_id_patient: int,
        response: Response,
):
    try:
        patient = Patients.get_or_none(id=updated_id_patient)

        if patient is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid patient ID",
            )
        else:
            appointment = Appointments.get_by_id(appointment_id)

            appointment.id_patient = updated_id_patient

            appointment.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)

    except Appointments.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


@router.put("/api/medicineProject/appointments/{appointment_id}/doctor_id")
async def update_appointment_doctor_id(
        appointment_id: int,
        updated_doctor_id: int,
        response: Response,
):
    try:
        doctor = Doctors.get_or_none(id=updated_doctor_id)

        if doctor is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid doctor ID",
            )
        else:
            appointment = Appointments.get_by_id(appointment_id)

            appointment.id_doctor = updated_doctor_id

            appointment.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)

    except Appointments.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


@router.put("/api/medicineProject/appointments/{appointment_id}/date")
async def update_appointment_date(
        appointment_id: int,
        updated_date: str,
        response: Response,
):
    try:
        if is_valid_date(updated_date):
            appointment = Appointments.get_by_id(appointment_id)

            appointment.date = updated_date

            appointment.save()

            response.status_code = status.HTTP_204_NO_CONTENT
            return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
        else:
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Validation error in input data",
            )

    except Appointments.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


@router.put("/api/medicineProject/appointments/{appointment_id}/status")
async def update_appointment_status(
        appointment_id: int,
        updated_status: str,
        response: Response,
):
    try:
        if is_valid_status(updated_status):
            appointment = Appointments.get_by_id(appointment_id)

            if appointment.status != updated_status:
                appointment.status = updated_status
                appointment.save()
                response.status_code = status.HTTP_204_NO_CONTENT
                return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
            else:
                response.status_code = status.HTTP_304_NOT_MODIFIED
                return JSONResponse(
                    content={"message": "Appointment status is already the same."},
                    status_code=status.HTTP_304_NOT_MODIFIED
                )
        else:
            response.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Validation error in input data",
            )

    except Appointments.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )


@router.delete("/api/medicineProject/appointments/{appointment_id}")
async def delete_appointment(appointment_id: int, response: Response):
    try:
        appointment = Appointments.get_by_id(appointment_id)

        appointment.delete_instance()

        response.status_code = status.HTTP_204_NO_CONTENT

    except Appointments.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found",
        )
