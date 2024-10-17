from fastapi import APIRouter, Response, HTTPException, status
from starlette.responses import JSONResponse

from DTO.validationDTO import *
from Databases.SQL.SQLDatabase import Patients, Doctors
from Databases.NoSQL.consultationDatabase import *

router = APIRouter()


def create_response_data(consultations):
    response_data = {}
    index = 0

    for consultation in consultations:
        response_data.update({
            f"consultation {str(index + 1)}": {
                "id": str(consultation['_id']),
                "id_patient": consultation['patient_id'],
                "id_doctor": consultation['doctor_id'],
                "date": consultation['date'],
                "diagnostic": consultation['diagnostic'],
                "links": {
                    "self": {
                        "href": f"/api/medicineProject/consultation/{str(consultation['_id'])}", "type": "GET"
                    },
                    "update_id_patient": {
                        "href": f"/api/medicineProject/consultation/{str(consultation['_id'])}/id_patient",
                        "type": "PUT"
                    },
                    "update_id_doctor": {
                        "href": f"/api/medicineProject/consultation/{str(consultation['_id'])}/id_doctor",
                        "type": "PUT"
                    },
                    "update_date": {
                        "href": f"/api/medicineProject/consultation/{str(consultation['_id'])}/date",
                        "type": "PUT"
                    },
                    "update_diagnostic": {
                        "href": f"/api/medicineProject/consultation/{str(consultation['_id'])}/diagnostic",
                        "type": "PUT"
                    },
                    "update_investigations": {
                        "href": f"/api/medicineProject/consultation/{str(consultation['_id'])}/investigations",
                        "type": "PUT"
                    },
                    "delete consultation": {
                        "href": f"/api/medicineProject/consultation/{str(consultation['_id'])}", "type": "DELETE"
                    }
                }
            }
        })
        index += 1

    return response_data


@router.post("/api/medicineProject/consultations/")
async def create_consultation(
        consultation: ConsultationDTO,
        response: Response,
):
    consultation_results = get_consultation_from_database(consultation.id_patient, consultation.id_doctor,
                                                          consultation.date, consultation.diagnostic)
    if is_valid_consultation(consultation):
        patient = Patients.get_or_none(cnp=consultation.id_patient)
        doctor = Doctors.get_or_none(id=consultation.id_doctor)

        if patient is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid patient ID",
            )
        elif doctor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid doctor ID",
            )
        elif len(consultation_results) != 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A consultation with these parameters already exits!",
            )
        else:
            response.status_code = status.HTTP_201_CREATED

            add_consultation_document(consultation.id_patient, consultation.id_doctor, consultation.date,
                                      consultation.diagnostic, consultation.investigations)
            new_consultation = get_consultation_from_database(consultation.id_patient, consultation.id_doctor,
                                                              consultation.date, consultation.diagnostic)

            response_data = create_response_data(new_consultation)

    else:
        response.status_code = status.HTTP_200_OK
        response_data = {
            "message": f"The consultation could not be registered due to errors in the input data!",
            "_links": {
                "view consultations": {
                    "href": "/api/medicineProject/consultation", "type": "GET",
                },
                "add new consultation": {
                    "href": "/api/medicineProject/consultation/create", "type": "POST",
                },
            }
        }

    return response_data


@router.get("/api/medicineProject/consultations/{patient_id}/{doctor_id}/date/diagnostic")
async def get_consultation(patient_id: int, doctor_id: int, date: str, diagnostic: str, response: Response):
    patient = Patients.get_or_none(id=patient_id)
    doctor = Doctors.get_or_none(id=doctor_id)

    if patient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid patient ID",
        )
    elif doctor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid doctor ID",
        )
    else:
        consultation = get_consultation_from_database(patient_id, doctor_id, date, diagnostic)

        if not consultation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The consultation with the given details could not be found!",
            )
        else:
            response.status_code = status.HTTP_200_OK

            response_data = create_response_data(consultation)

            return response_data


@router.get("/api/medicineProject/consultations/{patient_cnp}")
async def get_consultations_by_patient_id(patient_cnp: int, response: Response):
    patient = Patients.get_or_none(cnp=patient_cnp)

    if patient is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        response_data = {
            "message": "Invalid patient CNP",
        }
    else:
        consultations = get_consultations_by_attribute(patient_cnp, "patient_id")

        if not consultations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultations not found for the given patient CNP",
            )
        else:
            response.status_code = status.HTTP_200_OK

            response_data = create_response_data(consultations)

    return response_data


@router.get("/api/medicineProject/consultations/{doctor_id}")
async def get_consultations_by_doctor_id(doctor_id: int, response: Response):
    doctor = Doctors.get_or_none(id=doctor_id)

    if doctor is None:
        response.status_code = status.HTTP_404_NOT_FOUND
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid doctor ID",
        )
    else:
        consultations = get_consultations_by_attribute(doctor_id, "doctor_id")

        if not consultations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Consultations not found for the given doctor ID",
            )
        else:
            response.status_code = status.HTTP_200_OK

            response_data = create_response_data(consultations)

    return response_data


@router.get("/api/medicineProject/consultations/date/")
async def get_consultations_by_date(date: str, response: Response):
    consultations = get_consultations_by_attribute(date, "date")

    if not consultations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultations not found for date: {date}",
        )
    else:
        response.status_code = status.HTTP_200_OK

        response_data = create_response_data(consultations)

        return response_data


@router.get("/api/medicineProject/consultations/diagnostics/")
async def get_consultations_by_diagnostic(diagnostic: str, response: Response):
    consultations = get_consultations_by_attribute(diagnostic, "diagnostic")

    if not consultations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Consultations not found for diagnostic: {diagnostic}",
        )
    else:
        response.status_code = status.HTTP_200_OK

        response_data = create_response_data(consultations)

        return response_data


@router.get("/api/medicineProject/consultations/")
async def get_all_consultations(response: Response):
    consultations = get_consultations_by_attribute("", "")

    if len(consultations) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No appointments found",
        )
    else:
        response.status_code = status.HTTP_200_OK

        response_data = create_response_data(consultations)

        return response_data


@router.put("/api/medicineProject/consultations/")
async def update_consultation(
        existing_consultation: ConsultationDTO,
        new_consultation: ConsultationDTO,
        response: Response,
):
    if is_valid_consultation(new_consultation) and is_valid_consultation(existing_consultation):
        patient = Patients.get_or_none(cnp=existing_consultation.id_patient)
        doctor = Doctors.get_or_none(id=existing_consultation.id_doctor)
        new_patient = Patients.get_or_none(cnp=existing_consultation.id_patient)
        new_doctor = Doctors.get_or_none(id=existing_consultation.id_doctor)

        if patient is None and new_patient is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid patient CNP",
            )
        elif doctor is None and new_doctor is None:
            response.status_code = status.HTTP_404_NOT_FOUND
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid doctor ID",
            )
        else:
            if (existing_consultation.id_patient == new_consultation.id_patient and
                    existing_consultation.id_doctor == new_consultation.id_doctor and
                    existing_consultation.date == new_consultation.date and
                    existing_consultation == new_consultation.diagnostic):
                response.status_code = status.HTTP_304_NOT_MODIFIED
                raise HTTPException(
                    status_code=status.HTTP_200_OK,
                    detail="To update a consultation you must modify at least a parameter!",
                )
            else:
                existing_consultation = get_consultation_from_database(existing_consultation.id_patient,
                                                                       existing_consultation.id_doctor,
                                                                       existing_consultation.date,
                                                                       existing_consultation.diagnostic)
                if len(existing_consultation) == 0:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="The consultation with the given details could not been found!",
                    )
                else:
                    update_consultation_in_database(existing_consultation[0]['_id'], new_consultation.id_patient,
                                                    new_consultation.id_doctor,
                                                    new_consultation.date, new_consultation.diagnostic)

                    response.status_code = status.HTTP_204_NO_CONTENT
                    return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
    else:
        response.status_code = status.HTTP_200_OK
        response_data = {
            "message": f"The consultation could not be registered due to errors in the input data!",
            "_links": {
                "view consultations": {
                    "href": "/api/medicineProject/consultation", "type": "GET",
                },
                "add new consultation": {
                    "href": "/api/medicineProject/consultation/create", "type": "POST",
                },
            }
        }

        return response_data


@router.delete("/api/medicineProject/consultations/")
async def delete_consultation(
        consultation: ConsultationDTO,
        response: Response):
    if is_valid_consultation(consultation):
        patient = Patients.get_or_none(cnp=consultation.id_patient)
        doctor = Doctors.get_or_none(id=consultation.id_doctor)

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
            consultation = get_consultation_from_database(consultation.id_patient, consultation.id_doctor,
                                                          consultation.date, consultation.diagnostic)
            if len(consultation) == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="The consultation with the given details could not been found!",
                )
            else:
                delete_consultation_from_database(consultation[0]['_id'])

                response.status_code = status.HTTP_204_NO_CONTENT
                return JSONResponse(content=None, status_code=status.HTTP_204_NO_CONTENT)
    else:
        response.status_code = status.HTTP_200_OK
        response_data = {
            "message": f"The consultation could not be registered due to errors in the input data!",
            "_links": {
                "view consultations": {
                    "href": "/api/medicineProject/consultation", "type": "GET",
                },
                "add new consultation": {
                    "href": "/api/medicineProject/consultation/create", "type": "POST",
                },
            }
        }

        return response_data
