from pydantic import BaseModel, Field, EmailStr, model_validator, field_validator
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


class FlightDetails(BaseModel):
    flight_number: str = Field(..., min_length=3, max_length=10, description="Flight number")
    airline: str = Field(..., min_length=3, max_length=50, description="Airline name")
    origin_airport: str = Field(..., min_length=3, max_length=50, description="Origin airport code or name")
    destination_airport: str = Field(..., min_length=3, max_length=50, description="Destination airport code or name")
    departure_datetime: datetime = Field(..., description="Departure date and time")
    arrival_datetime: datetime = Field(..., description="Arrival date and time")
    seat_information: str = Field(..., pattern="^[0-9]{1,2}[A-Z]{1}$", description="Seat number")
    travel_class: str = Field(..., pattern="^(economy|business|first)$", description="Class of travel")


class Reservation(BaseModel):
    id: int = Field(default=None)
    passenger_info: PassengerInfo
    flight_details: FlightDetails
    total_price: float = Field(..., gt=0, description="Total price of the reservation")
    reservation_status: str = Field(..., pattern="^(confirmed|pending|cancelled)$", description="Status of the reservation")
    creation_timestamp: datetime = Field(description="Timestamp when the reservation was created")
    last_update_timestamp: datetime = Field(description="Timestamp when the reservation was last updated")

    def __eq__(self, other):
        if not isinstance(other, Reservation):
            raise NotImplemented('Cannot compare Reservation objects to objects with other datatype')
        return (
            self.flight_details.flight_number == other.flight_details.flight_number and
            self.passenger_info.id == other.passenger_info.id
        )

    @model_validator(mode='before')
    @classmethod
    def add_timestamp(cls, values):
        if 'creation_timestamp' in values.keys() or 'last_update_timestamp' in values.keys():
            raise Exception('creation timestamp and last update timestamp cant be in the request!')
        values['creation_timestamp'] = values['last_update_timestamp'] = datetime.now()
        return values