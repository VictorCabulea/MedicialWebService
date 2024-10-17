from datetime import datetime

import pymongo
from bson import ObjectId


def add_consultation_document(patient_id, doctor_id, date, diagnostic, investigations):
    client = pymongo.MongoClient("mongodb://localhost:27017/")

    database = client["medicineProjectNoSQL"]

    consultation_collection = database["consultatii"]

    consultation_document = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "date": date,
        "diagnostic": diagnostic,
        "investigations": investigations
    }

    consultation_collection.insert_one(consultation_document)

    client.close()


def get_consultations_by_attribute(searched, attribute):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client["medicineProjectNoSQL"]
    consultation_collection = database["consultatii"]

    consultations = []

    if attribute == "":
        consultations = list(consultation_collection.find({}))
    if attribute == "patient_id":
        consultations = list(consultation_collection.find({"patient_id": searched}))
    if attribute == "doctor_id":
        consultations = list(consultation_collection.find({"doctor_id": searched}))
    if attribute == "diagnostic":
        consultations = list(consultation_collection.find({"diagnostic": searched}))
    if attribute == "date":
        consultations = list(consultation_collection.find({"date": searched}))

    consultations.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))

    return consultations


def get_consultation_from_database(patient_id, doctor_id, date, diagnostic):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client["medicineProjectNoSQL"]
    consultation_collection = database["consultatii"]

    consultations = list(consultation_collection.find({"patient_id": patient_id, "doctor_id": doctor_id, "date": date,
                                                       "diagnostic": diagnostic}))

    return consultations


def update_consultation_in_database(consultation_id, new_patient_id, new_doctor_id, new_date, new_diagnostic):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client["medicineProjectNoSQL"]
    consultation_collection = database["consultatii"]

    result = consultation_collection.update_one(
        {'_id': ObjectId(consultation_id)},
        {
            '$set': {
                'patient_id': new_patient_id,
                'doctor_id': new_doctor_id,
                'date': new_date,
                'diagnostic': new_diagnostic
            }
        }
    )


def delete_consultation_from_database(consultation_id):
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    database = client["medicineProjectNoSQL"]
    consultation_collection = database["consultatii"]

    result = consultation_collection.delete_one({'_id': ObjectId(consultation_id)})

    if result.deleted_count == 1:
        print(f"Consultation deleted successfully: {consultation_id}")
        return True
    else:
        print(f"Deletion failed. Consultation not found: {consultation_id}")
        return False
