from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import List
import uuid

app = FastAPI()


class PassengerInfo(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Automatically generated reservation ID")
    full_name: str = Field(..., min_length=3, max_length=100, description="Full name of the passenger")
    email: EmailStr = Field(..., description="Email address of the passenger")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number of the passenger")


class FlightDetails(BaseModel):
    flight_number: str = Field(..., min_length=3, max_length=10, description="Flight number")
    airline: str = Field(..., min_length=3, max_length=50, description="Airline name")
    origin_airport: str = Field(..., min_length=3, max_length=50, description="Origin airport code or name")
    destination_airport: str = Field(..., min_length=3, max_length=50, description="Destination airport code or name")
    departure_datetime: datetime = Field(..., description="Departure date and time")
    arrival_datetime: datetime = Field(..., description="Arrival date and time")
    seat_information: str = Field(..., min_length=1, max_length=5, description="Seat number")
    travel_class: str = Field(..., pattern="^(economy|business|first)$", description="Class of travel")


class Reservation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Automatically generated reservation ID")
    passenger_info: PassengerInfo
    flight_details: FlightDetails
    total_price: float = Field(..., gt=0, description="Total price of the reservation")
    reservation_status: str = Field(..., pattern="^(confirmed|pending|cancelled)$", description="Status of the reservation")
    creation_timestamp: datetime = Field(description="Timestamp when the reservation was created")
    last_update_timestamp: datetime = Field(description="Timestamp when the reservation was last updated")


reservations = []


@app.post("/reservations", response_model=Reservation)
async def create_reservation(reservation: Reservation):
    for existing_reservation in reservations:
        if existing_reservation.id == reservation.id:
            raise HTTPException(status_code=400, detail="Reservation with this ID already exists.")
    reservations.append(reservation)
    return reservation


@app.get("/reservations", response_model=List[Reservation])
async def get_reservations():
    return reservations


@app.get("/reservations/{reservation_id}", response_model=Reservation)
async def get_reservation_by_id(reservation_id: int):
    for reservation in reservations:
        if reservation.id == reservation_id:
            return reservation
    raise HTTPException(status_code=404, detail="Reservation not found.")


@app.put("/reservations/{reservation_id}", response_model=Reservation)
async def update_reservation(reservation_id: int, updated_reservation: Reservation):
    for index, reservation in enumerate(reservations):
        if reservation.id == reservation_id:
            reservations[index] = updated_reservation
            return updated_reservation
    raise HTTPException(status_code=404, detail="Reservation not found.")


@app.delete("/reservations/{reservation_id}", response_model=dict)
async def delete_reservation(reservation_id: int):
    for index, reservation in enumerate(reservations):
        if reservation.id == reservation_id:
            reservations.pop(index)
            return {"message": "Reservation deleted successfully."}
    raise HTTPException(status_code=404, detail="Reservation not found.")
