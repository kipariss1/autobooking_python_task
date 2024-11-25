from pydantic import BaseModel, Field, EmailStr, field_validator
import re
from datetime import datetime


class PassengerInfo(BaseModel):
    id: int = Field(default=None)
    full_name: str = Field(..., min_length=3, max_length=100, description="Full name of the passenger")
    email: EmailStr = Field(..., description="Email address of the passenger")
    phone_number: str = Field(..., min_length=10, max_length=15, description="Phone number of the passenger")

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value):
        if not re.match(r"^[a-zA-Z\s'-]+$", value):
            raise ValueError("Full name must contain only letters, spaces, hyphens, or apostrophes.")
        if len(value.split()) < 2:
            raise ValueError("Full name must include at least a first and last name.")
        return value.strip()

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        if not re.match(r"^\+?[0-9]{9,15}$", value):
            raise ValueError("Phone number must contain only digits and may include an optional '+' prefix.")
        return value.strip()

    class Config:
        from_attributes = True


class FlightDetails(BaseModel):
    flight_number: str = Field(..., min_length=3, max_length=10, description="Flight number")
    airline: str = Field(..., min_length=3, max_length=50, description="Airline name")
    origin_airport: str = Field(..., min_length=3, max_length=50, description="Origin airport code or name")
    destination_airport: str = Field(..., min_length=3, max_length=50, description="Destination airport code or name")
    departure_datetime: datetime = Field(..., description="Departure date and time")
    arrival_datetime: datetime = Field(..., description="Arrival date and time")
    seat_information: str = Field(..., pattern="^[0-9]{1,2}[A-Z]{1}$", description="Seat number")
    travel_class: str = Field(..., pattern="^(economy|business|first)$", description="Class of travel")

    class Config:
        from_attributes = True


class Reservation(BaseModel):

    id: int = Field(default=None)
    passenger_info: PassengerInfo = Field(...)
    flight_details: FlightDetails = Field(...)
    total_price: float = Field(..., gt=0, description="Total price of the reservation")
    reservation_status: str = Field(..., pattern="^(confirmed|pending|cancelled)$", description="Status of the reservation")

    class Config:
        from_attributes = True


class ReservationOut(BaseModel):

    id: int = Field(default=None)
    passenger_info_id: int
    flight_details_id: int
    passenger_info: PassengerInfo = Field(...)
    flight_details: FlightDetails = Field(...)
    total_price: float = Field(..., gt=0, description="Total price of the reservation")
    reservation_status: str = Field(..., pattern="^(confirmed|pending|cancelled)$", description="Status of the reservation")
    creation_timestamp: datetime = Field(description="Timestamp when the reservation was created")
    last_update_timestamp: datetime = Field(description="Timestamp when the reservation was last updated")

    class Config:
        from_attributes = True
