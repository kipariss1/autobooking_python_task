from fastapi import FastAPI, HTTPException, Depends
import schemas
import uvicorn
from sqlalchemy.orm import Session
import models
from database import get_db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

app = FastAPI()


@app.post("/reservations")
async def create_reservation(reservation: schemas.Reservation, db: Session = Depends(get_db)):
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
    return schemas.ReservationOut.model_validate(new_reservation)


@app.get("/reservations")
async def get_reservations(db: Session = Depends(get_db)):
    reservations = db.query(models.Reservation).all()
    return [schemas.ReservationOut.model_validate(reservation) for reservation in reservations]


@app.get("/reservations/{reservation_id}")
async def get_reservation_by_id(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    return schemas.ReservationOut.model_validate(reservation)


def _check_and_update(
        model, model_attr: str, orig_db_resvtn, orig_attr: str, new_resvtn, attr_to_check: str, db: Session
):
    if getattr(new_resvtn, attr_to_check):
        db_obj = db.query(model).filter(
            getattr(model, model_attr) == getattr(orig_db_resvtn, orig_attr)
        ).first()
        if not db_obj:
            raise HTTPException(
                status_code=404, detail=f"{str(model)} associated with the reservation not found"
            )
        for attr, val in getattr(new_resvtn, attr_to_check).model_dump().items():
            setattr(getattr(orig_db_resvtn, attr_to_check), attr, val)


@app.put("/reservations/{reservation_id}")
async def update_reservation(
        reservation_id: int,
        reservation: schemas.Reservation,
        db: Session = Depends(get_db)
):
    old_reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()

    if not old_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")

    # Update PassengerInfo
    _check_and_update(
        models.PassengerInfo, 'id', old_reservation, 'passenger_info_id', reservation, 'passenger_info', db
    )
    _check_and_update(
        models.FlightDetails, 'id', old_reservation, 'flight_details_id', reservation, 'flight_details', db
    )
    # Update Reservation fields
    for attr, value in reservation.model_dump().items():
        if attr not in ("passenger_info", "flight_details", "id"):
            setattr(old_reservation, attr, value)
    # Update the timestamps
    old_reservation.last_update_timestamp = datetime.now()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Failed to update reservation: integrity error")
    db.refresh(old_reservation)
    return schemas.Reservation.model_validate(old_reservation)


@app.delete("/reservations/{reservation_id}", response_model=dict)
async def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    db.delete(reservation)
    db.commit()

    return {"message": "Reservation deleted successfully"}


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8000)
