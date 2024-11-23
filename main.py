from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr, model_validator
from functools import wraps
from datetime import datetime
from typing import List, Optional
import uvicorn

app = FastAPI()


class PassengerInfo(BaseModel):
    id: int = Field(default=None)
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
    id: int = Field(default=None)
    passenger_info: PassengerInfo
    flight_details: FlightDetails
    total_price: float = Field(..., gt=0, description="Total price of the reservation")
    reservation_status: str = Field(..., pattern="^(confirmed|pending|cancelled)$", description="Status of the reservation")
    creation_timestamp: datetime = Field(description="Timestamp when the reservation was created")
    last_update_timestamp: datetime = Field(description="Timestamp when the reservation was last updated")

    @model_validator(mode='before')
    @classmethod
    def create_or_update_with_timestamp(cls, values):
        if 'creation_timestamp' in values.keys() or 'last_update_timestamp' in values.keys():
            raise Exception('creation timestamp and last update timestamp cant be in the request!')
        values['creation_timestamp'] = values['last_update_timestamp'] = datetime.now()
        return values


reservations: List[Reservation] = []


def update_id():
    curr_id = len(reservations)
    reservations[-1].id = curr_id


# TODO: unify decorator for POST and for PUT
def post_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        res: Reservation = await func(*args, **kwargs)
        if not res.id:
            update_id()
        return res
    return wrapper


@app.post("/reservations", response_model=Reservation)
async def create_reservation(reservation: Reservation):
    for existing_reservation in reservations:
        # TODO: check here id of the passenger and number of flight instead of just checking the id
        if existing_reservation.passenger_info.id == reservation.passenger_info.id:
            raise HTTPException(status_code=400, detail="Reservation for this passenger already exists.")
    reservations.append(reservation)
    update_id()
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
            orig_creation_timestamp = reservations[index].creation_timestamp
            reservations[index] = updated_reservation
            reservations[index].id = reservation_id
            reservations[index].creation_timestamp = orig_creation_timestamp
            return updated_reservation
    raise HTTPException(status_code=404, detail="Reservation not found.")


@app.delete("/reservations/{reservation_id}", response_model=dict)
async def delete_reservation(reservation_id: int):
    for index, reservation in enumerate(reservations):
        if reservation.id == reservation_id:
            reservations.pop(index)
            return {"message": "Reservation deleted successfully."}
    raise HTTPException(status_code=404, detail="Reservation not found.")


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
