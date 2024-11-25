import time
from datetime import datetime
import pytest
from src.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app
import json
from unittest.mock import AsyncMock
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
def mock_send_notifications(monkeypatch):
    mock_send_notifications = AsyncMock()
    monkeypatch.setattr('src.email_notify.send_notification', mock_send_notifications)
    yield
    mock_send_notifications.reset_mock()


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
      "reservation_status": "confirmed"
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


def test__unathorised(reservation_passenger_kirill, test_db, add_mock_users):
    assert client.get('/reservations').status_code == 401
    assert client.post(
        '/reservations',
        json=reservation_passenger_kirill
    ).status_code == 401
    client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('kirill', 'mypass')
    )
    assert client.put('/reservations/1', json=reservation_passenger_kirill).status_code == 401
    assert client.delete('/reservations/1').status_code == 401


def test__authorised_submit_the_reservation(reservation_passenger_kirill, test_db, add_mock_users, mock_users):
    res = client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('kirill', 'mypass')
    )
    res = json.loads(res.content)
    assert res['auth_user_id'] == mock_users.index({"username": "kirill", "password": "bXlwYXNz"}) + 1
    assert res['passenger_info']['full_name'] == 'Kirill Rass'
    assert res['total_price'] == 99.99
    assert res["reservation_status"] == "confirmed"


def test__assert_put_updated_the_reservation(reservation_passenger_kirill, test_db, add_mock_users, mock_users):
    res = client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('kirill', 'mypass')
    )
    res = json.loads(res.content)
    id = res['id']
    updated_reservation = deepcopy(reservation_passenger_kirill)
    updated_reservation['passenger_info']['full_name'] = 'Alex Smith'
    time.sleep(2)
    res_upd = client.put(
        f'/reservations/{id}',
        json=updated_reservation,
        auth=('kirill', 'mypass')
    )
    res_upd = json.loads(res_upd.content)
    assert res_upd['id'] == id
    assert res_upd['passenger_info']['full_name'] == 'Alex Smith'
    assert datetime.fromisoformat(res_upd['creation_timestamp']) == datetime.fromisoformat(res['creation_timestamp'])
    assert datetime.fromisoformat(res_upd['last_update_timestamp']) \
           > datetime.fromisoformat(res_upd['creation_timestamp'])


def test__assert_reservation_already_created(reservation_passenger_kirill, test_db, add_mock_users, mock_users):
    res = client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('kirill', 'mypass')
    )
    assert client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('claradavis', 'mypass')
    ).status_code == 400


def test__assert_authorisation_on_put(reservation_passenger_kirill, test_db, add_mock_users, mock_users):
    res = client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('kirill', 'mypass')
    )
    res = json.loads(res.content)
    id = res['id']
    updated_reservation = deepcopy(reservation_passenger_kirill)
    updated_reservation['passenger_info']['full_name'] = 'Alex Smith'
    time.sleep(2)
    assert client.put(
        f'/reservations/{id}',
        json=updated_reservation,
        auth=('claradavis', 'mypass')
    ).status_code == 404


def test__assert_autorization_on_get(
        reservation_passenger_kirill, reservation_passenger_claradavis, test_db, add_mock_users, mock_users
):
    assert client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('kirill', 'mypass')
    ).status_code == 200

    assert client.post(
        '/reservations',
        json=reservation_passenger_claradavis,
        auth=('claradavis', 'mypass')
    ).status_code == 200

    assert len(json.loads(client.get('/reservations', auth=('kirill', 'mypass')).content)) == 1
    assert len(json.loads(client.get('/reservations', auth=('claradavis', 'mypass')).content)) == 1
    assert client.get('/reservations/1', auth=('kirill', 'mypass')).status_code == 200
    assert client.get('/reservations/2', auth=('kirill', 'mypass')).status_code == 404
    assert client.get('/reservations/1', auth=('claradavis', 'mypass')).status_code == 404
    assert client.get('/reservations/2', auth=('claradavis', 'mypass')).status_code == 200


def test__assert_authorization_on_delete(
        reservation_passenger_kirill, reservation_passenger_claradavis, test_db, add_mock_users, mock_users
):
    assert client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('kirill', 'mypass')
    ).status_code == 200

    assert client.post(
        '/reservations',
        json=reservation_passenger_claradavis,
        auth=('claradavis', 'mypass')
    ).status_code == 200

    assert client.delete('/reservations/1', auth=('kirill', 'mypass')).status_code == 200
    assert client.delete('/reservations/2', auth=('kirill', 'mypass')).status_code == 404
    assert client.delete('/reservations/1', auth=('claradavis', 'mypass')).status_code == 404
    assert client.delete('/reservations/2', auth=('claradavis', 'mypass')).status_code == 200

    assert len(json.loads(client.get('/reservations', auth=('kirill', 'mypass')).content)) == 0
    assert len(json.loads(client.get('/reservations', auth=('claradavis', 'mypass')).content)) == 0


