import pytest
from database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app
import json
import models


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


def test__unathorised(reservation_passenger_kirill, test_db, add_mock_users):
    assert client.get('/reservations').status_code == 401
    assert client.post(
        '/reservations',
        json=reservation_passenger_kirill
    ).status_code == 401


def test__authorised_submit_the_reservation(reservation_passenger_kirill, test_db, add_mock_users, mock_users):
    res = client.post(
        '/reservations',
        json=reservation_passenger_kirill,
        auth=('kirill', 'mypass')
    )
    res = json.loads(res.content)
    assert res['auth_user_id'] == mock_users.index({"username": "kirill", "password": "bXlwYXNz"}) + 1


def test__assert_put_updated_the_reservation():
    # TODO: make second tests
    pass


