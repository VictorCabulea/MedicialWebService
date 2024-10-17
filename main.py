import uvicorn
from fastapi import FastAPI
from APIs import patientAPI, doctorAPI, appointmentAPI, consultationAPI, accountAPI

app = FastAPI()

app.include_router(patientAPI.router)
app.include_router(doctorAPI.router)
app.include_router(appointmentAPI.router)
app.include_router(consultationAPI.router)
app.include_router(accountAPI.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
