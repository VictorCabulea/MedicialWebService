import peewee
from peewee import Model, MySQLDatabase

db = MySQLDatabase('medicineProject', user='root', password='victor', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = db


class Doctors(BaseModel):
    last_name = peewee.CharField(max_length=30)
    first_name = peewee.CharField(max_length=30)
    email = peewee.CharField(max_length=50)
    phone_number = peewee.CharField(max_length=10)
    speciality = peewee.CharField(max_length=30)

    @classmethod
    def get_by_name(cls, last_name, first_name):
        try:
            doctor = cls.filter((cls.first_name == first_name) & (cls.last_name == last_name)).get()
            return doctor
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_email(cls, email):
        try:
            doctor = cls.get(cls.email == email)
            return doctor
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_phone_number(cls, phone_number):
        try:
            doctor = cls.get(cls.phone_number == phone_number)
            return doctor
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_speciality(cls, speciality):
        try:
            doctor = cls.get(cls.speciality == speciality)
            return doctor
        except cls.DoesNotExist:
            return None


class Patients(BaseModel):
    cnp = peewee.CharField(max_length=13, primary_key=True)
    lastName = peewee.CharField(max_length=30)
    firstName = peewee.CharField(max_length=30)
    email = peewee.CharField(max_length=50)
    phoneNumber = peewee.CharField(max_length=10)
    age = peewee.IntegerField()
    birthday = peewee.DateField()
    is_active = peewee.BooleanField()

    @classmethod
    def get_by_cnp(cls, cnp):
        try:
            patient = cls.get(cls.cnp == cnp)
            return patient
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_email(cls, email):
        try:
            patient = cls.get(cls.email == email)
            return patient
        except cls.DoesNotExist:
            return None

    @classmethod
    def get_by_phone_number(cls, phoneNumber):
        try:
            patient = cls.get(cls.phoneNumber == phoneNumber)
            return patient
        except cls.DoesNotExist:
            return None

class Appointments(BaseModel):
    id_patient = peewee.ForeignKeyField(Patients, backref='appointments')
    id_doctor = peewee.ForeignKeyField(Doctors, backref='appointments')
    date = peewee.DateField(formats='%d %m %Y')
    status = peewee.CharField(max_length=30)


class Accounts(BaseModel):
    last_name = peewee.CharField(max_length=30)
    first_name = peewee.CharField(max_length=30)
    user_name = peewee.CharField(max_length=30)
    user_email = peewee.CharField(max_length=30)
    password = peewee.CharField(max_length=30)


db.connect()
db.create_tables([Doctors, Patients, Appointments, Accounts], safe=True)
