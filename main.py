from fastapi import FastAPI, HTTPException, Depends
from schemas import Reservation
from typing import List
import uvicorn
from sqlalchemy.orm import Session
import models
from database import get_db
from datetime import datetime

app = FastAPI()


reservations: List[Reservation] = []


def update_id():
    curr_id = len(reservations)
    reservations[-1].id = curr_id


def save_reservation(db: Session, reservation: Reservation, reservation_id: int = None):
    if not reservation_id:  # POST
        existing_reservation = db.query(models.Reservation).join(models.FlightDetails).filter(
            models.Reservation.passenger_info_id == reservation.passenger_info.id,
            models.FlightDetails.flight_number == reservation.flight_details.flight_number
        ).first()

        if existing_reservation:
            raise HTTPException(status_code=400, detail="Reservation already exists for this passenger and flight.")
        passenger = db.query(models.PassengerInfo).filter(
            models.PassengerInfo.id == reservation.passenger_info.id
        ).first()
        if not passenger:
            passenger = models.PassengerInfo(**reservation.passenger_info.dict())
            db.add(passenger)
            db.commit()
            db.refresh(passenger)

        # Create FlightDetails record if not already present
        flight = db.query(models.FlightDetails).filter(
            models.FlightDetails.flight_number == reservation.flight_details.flight_number
        ).first()
        if not flight:
            flight = models.FlightDetails(**reservation.flight_details.dict())
            db.add(flight)
            db.commit()
            db.refresh(flight)

        # Create a new Reservation record
        new_reservation = models.Reservation(
            total_price=reservation.total_price,
            reservation_status=reservation.reservation_status,
            passenger_info_id=passenger.id,
            flight_details_id=flight.id
        )
        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)
        db.refresh(new_reservation.flight_details)
        db.refresh(new_reservation.passenger_info)

        reservation.id = new_reservation.id
        reservation.creation_timestamp = new_reservation.creation_timestamp
        reservation.last_update_timestamp = new_reservation.last_update_timestamp

        return reservation
    else:                   # PUT
        for index, old_reservation in enumerate(reservations):
            if old_reservation.id == reservation_id:
                orig_creation_timestamp = reservations[index].creation_timestamp
                reservation.id = reservation_id
                reservation.creation_timestamp = orig_creation_timestamp
                reservations[index] = reservation
                return reservations[index]
        raise HTTPException(status_code=404, detail="Reservation not found.")


@app.post("/reservations", response_model=Reservation)
async def create_reservation(reservation: Reservation, db: Session = Depends(get_db)):
    return save_reservation(db, reservation)


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
async def update_reservation(reservation_id: int, updated_reservation: Reservation, db: Session = Depends(get_db)):
    return save_reservation(db, updated_reservation, reservation_id)


@app.delete("/reservations/{reservation_id}", response_model=dict)
async def delete_reservation(reservation_id: int):
    for index, reservation in enumerate(reservations):
        if reservation.id == reservation_id:
            reservations.pop(index)
            return {"message": "Reservation deleted successfully."}
    raise HTTPException(status_code=404, detail="Reservation not found.")


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
