from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime


Base = declarative_base()


class PassengerInfo(Base):
    __tablename__ = 'passenger_info'

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(15), nullable=False)

    reservations = relationship("Reservation", back_populates="passenger_info")


class FlightDetails(Base):
    __tablename__ = 'flight_details'

    id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String(10), nullable=False)
    airline = Column(String(50), nullable=False)
    origin_airport = Column(String(50), nullable=False)
    destination_airport = Column(String(50), nullable=False)
    departure_datetime = Column(DateTime, nullable=False)
    arrival_datetime = Column(DateTime, nullable=False)
    seat_information = Column(String(5), nullable=False)
    travel_class = Column(String(10), nullable=False)

    # Relationship to Reservation
    reservations = relationship("Reservation", back_populates="flight_details")


class Reservation(Base):
    __tablename__ = 'reservations'

    id = Column(Integer, primary_key=True, index=True)
    total_price = Column(Float, nullable=False)
    reservation_status = Column(String(20), nullable=False)  # confirmed, pending, cancelled
    creation_timestamp = Column(DateTime, default=datetime.utcnow)
    last_update_timestamp = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    passenger_info_id = Column(Integer, ForeignKey('passenger_info.id'), nullable=False)
    flight_details_id = Column(Integer, ForeignKey('flight_details.id'), nullable=False)

    passenger_info = relationship("PassengerInfo", back_populates="reservations")
    flight_details = relationship("FlightDetails", back_populates="reservations")
