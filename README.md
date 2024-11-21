# Flight Reservation API Implementation Task

## Objective
Create a RESTful API using Python that manages flight reservations. The API should allow users to create, read, update, and delete flight reservations.

## Requirements

### 1. Technology Stack
- Use a modern Python web framework.
- Preferably utilize technical stack mentioned in Job posting.
- Usage of AI based assistant is permitted and encouraged, but own your code.
- Prepare your application to run in an isolated, containerized environment suitable for deployment across various systems.

### 2. API Endpoints
Implement the following endpoints:
- `POST /reservations` - Create a new flight reservation
- `GET /reservations` - Retrieve a list of all reservations
- `GET /reservations/{reservation_id}` - Retrieve a specific reservation by ID
- `PUT /reservations/{reservation_id}` - Update an existing reservation
- `DELETE /reservations/{reservation_id}` - Delete a reservation

### 3. Reservation Model
Each reservation should include the following information:
- Reservation ID (automatically generated)
- Passengers Information:
  - Full name
  - Email
  - Phone number
- Flight Details:
  - Flight number
  - Airline
  - Origin airport
  - Destination airport
  - Departure date and time
  - Arrival date and time
- Seat information
- Class (e.g., economy, business, first)
- Total price
- Reservation status (e.g., confirmed, pending, cancelled)
- Creation timestamp
- Last update timestamp

### 4. Implementation Details
- Implement input validation and error handling.
- Use an in-memory data store or a standalone relational DB
- Implement basic authentication for the API.
- Implement tests.
- Provide documentation (readme).

### 5. Async notification feature
- Simulate sending email notifications to passengers about their reservation status
- Trigger the notification when reservation is created or its status is updated
- Use a mock server (such as RequestBin, webhook.site, or httpbin.org) to test this functionality
- Implement using Python's async/await syntax

## Submission Guidelines
1. Provide the source code in a GitHub/Gitlab repository.
2. Include a README file with instructions on how to set up and run the API.
3. Provide example curl commands or a Postman collection to demonstrate the API usage.
