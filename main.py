from fastapi import FastAPI, HTTPException, Depends
from validation_models import Reservation
from typing import List
import uvicorn
from sqlalchemy.orm import Session
import models
from database import get_db

app = FastAPI()


reservations: List[Reservation] = []


def update_id():
    curr_id = len(reservations)
    reservations[-1].id = curr_id


def save_reservation(db: Session, reservation: Reservation, reservation_id: int = None):
    existing_reservations = db.query(models.Reservation).all()
    if not reservation_id:  # POST
        # TODO: redo this for sqlalchemy
        for existing_reservation in existing_reservations:
            if existing_reservation == reservation:
                raise HTTPException(status_code=400, detail="Reservation for this passenger already exists.")
        db_reservation = models.Reservation(**reservation.dict())
        db.add(db_reservation)
        db.commit()
        db.refresh(db_reservation)
        update_id()
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
    return reservation


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
