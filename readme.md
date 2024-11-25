# Autobooking task

Autobooking task

---

Project, which complies to the requirements.md

---

## Setup Instructions

### Prerequisites

- Python 3.12
- docker

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd <repository-folder>

2. **Make venv & install packages**:
   ```bash
   python -m venv .venv
   pip install -r requirements.txt

3. **Run app or run container**:
   ```bash
   uvicorn main:app --reload --host <your-host> --port <your-port>
   OR
   docker compose up --build

### Description

**Database**:

There is already sqlite local.db in the git which is empty except for table auth_users
which contains users for authentification:

| **Username** | **Password** |
|--------------|--------------|
| admin        | admin        |
| kirill       | mypass       |
| claradavis   | mypass       |

**Endpoints**:
- `POST /reservations` - Creates a new flight reservation
- `GET /reservations` - Retrieves a list of all reservations
- `GET /reservations/{reservation_id}` - Retrieves a specific reservation by ID
- `PUT /reservations/{reservation_id}` - Updates an existing reservation
- `DELETE /reservations/{reservation_id}` - Deletes a reservation

All endpoints are accessable only with Basic Auth, so you need to use one of the defined users or add yours. Authorised user can access, delete, update only reservations, made by him. 

**E-mail notifications**:

E-mail notifications are sended to the dummy server: httpbin.org to simulate the request to the real E-Mail server. It is sended on the creation of the reservation and on update of the status of the reservation.

### TechStack
- fastapi
- sqlalchemy with sqlite
- uvicorn as a server
- docker for containerisation
