import pytest
from database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from main import app
import schemas
import models

client = TestClient(app)


@pytest.fixture(scope="function")
def test_db():
    # Setup test database
    test_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(autouse=True)
def clean_test_db(test_db):
    # Truncate tables or reset DB state
    for table in reversed(Base.metadata.sorted_tables):
        test_db.execute(table.delete())
    test_db.commit()

@pytest.fixture
def insert_new_user(test_db):
    new_user = models.AuthUser(username="claradavis", password="bXlwYXNz")
    test_db.add(new_user)
    test_db.commit()
    test_db.refresh(new_user)
    return new_user


def test__unathorised():
    assert client.get('/reservations').status_code == 401
    assert client.post('/reservations', content=schemas.Reservation(**{
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
    )).status_code == 401


