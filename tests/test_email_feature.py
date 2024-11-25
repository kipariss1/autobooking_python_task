import pytest
from src.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app
from unittest.mock import AsyncMock, call, patch
from src import models
from copy import deepcopy


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        Base.metadata.create_all(bind=db.bind)
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def mock_users():
    return [
        {"username": "admin", "password": "YWRtaW4="},
        {"username": "kirill", "password": "bXlwYXNz"},
        {"username": "claradavis", "password": "bXlwYXNz"}
    ]


@pytest.fixture
def add_mock_users(mock_users):
    db = next(override_get_db())
    for user_data in mock_users:
        user = models.AuthUser(username=user_data["username"], password=user_data["password"])
        db.add(user)
    db.commit()


@pytest.fixture
def reservation_passenger_kirill():
    return {
      "passenger_info": {
        "id": 1,
        "full_name": "Kirill Rass",
        "email": "kirill.rass@example.com",
        "phone_number": "+12123334455"
      },
      "flight_details": {
        "flight_number": "UA789",
        "airline": "United Airlines",
        "origin_airport": "SFO",
        "destination_airport": "SEA",
        "departure_datetime": "2024-12-15T09:00:00",
        "arrival_datetime": "2024-12-15T11:15:00",
        "seat_information": "22F",
        "travel_class": "economy"
      },
      "total_price": 99.99,
      "reservation_status": "pending"
    }


@pytest.fixture
def reservation_passenger_claradavis():
    return {
      "passenger_info": {
        "id": 1,
        "full_name": "Clara Davis",
        "email": "clara.davis@example.com",
        "phone_number": "+12123334456"
      },
      "flight_details": {
        "flight_number": "UA799",
        "airline": "United Airlines",
        "origin_airport": "SFA",
        "destination_airport": "EEA",
        "departure_datetime": "2024-12-15T09:00:00",
        "arrival_datetime": "2024-12-15T11:15:00",
        "seat_information": "22F",
        "travel_class": "economy"
      },
      "total_price": 199.99,
      "reservation_status": "confirmed"
    }


def test__email_send_on_creation(reservation_passenger_kirill, test_db, add_mock_users, mock_users, monkeypatch):
    mock_send_notification = AsyncMock()
    with patch('src.email_notify.send_notification', mock_send_notification):
        assert client.post(
            '/reservations',
            json=reservation_passenger_kirill,
            auth=('kirill', 'mypass')
        ).status_code == 200
        assert call(
            'kirill.rass@example.com', 'Dear Kirill Rass, your reservation has been created. Details: Flight UA789, Status: pending.'
        ) in mock_send_notification.mock_calls


def test__email_send_on_update_status(reservation_passenger_kirill, test_db, add_mock_users, mock_users, monkeypatch):
    mock_send_notification = AsyncMock()
    with patch('src.email_notify.send_notification', mock_send_notification):
        assert client.post(
            '/reservations',
            json=reservation_passenger_kirill,
            auth=('kirill', 'mypass')
        ).status_code == 200

        updated_reservation = deepcopy(reservation_passenger_kirill)
        updated_reservation['reservation_status'] = 'confirmed'
        assert client.put(
            f'/reservations/1',
            json=updated_reservation,
            auth=('kirill', 'mypass')
        ).status_code == 200

        assert call(
            'kirill.rass@example.com',
            'Dear Kirill Rass, your reservation has been updated. Details: Flight UA789, Status: confirmed.'
        ) in mock_send_notification.mock_calls


def test__email_not_send_on_regular_update(reservation_passenger_kirill, test_db, add_mock_users, mock_users, monkeypatch):
    mock_send_notification = AsyncMock()
    with patch('src.email_notify.send_notification', mock_send_notification):
        assert client.post(
            '/reservations',
            json=reservation_passenger_kirill,
            auth=('kirill', 'mypass')
        ).status_code == 200

        updated_reservation = deepcopy(reservation_passenger_kirill)
        updated_reservation['total_price'] = 299.99
        assert client.put(
            f'/reservations/1',
            json=updated_reservation,
            auth=('kirill', 'mypass')
        ).status_code == 200
        assert call(
            'kirill.rass@example.com',
            'Dear Kirill Rass, your reservation has been created. Details: Flight UA789, Status: pending.'
        ) in mock_send_notification.mock_calls
        assert not call(
            'kirill.rass@example.com',
            'Dear Kirill Rass, your reservation has been updated. Details: Flight UA789, Status: confirmed.'
        ) in mock_send_notification.mock_calls
