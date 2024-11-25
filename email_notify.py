import httpx
from fastapi import HTTPException
from functools import wraps


mock_url = "https://httpbin.org/post"


async def send_notification(email: str, message: str):
    payload = {
        "email": email,
        "message": message
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(mock_url, json=payload)
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send notification to {email}: {response.text}"
            )


def notify_user(action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result, send_notification_flag = await func(*args, **kwargs)
            reservation = result
            email = reservation.passenger_info.email
            message = (
                f"Dear {reservation.passenger_info.full_name}, your reservation has been {action}. "
                f"Details: Flight {reservation.flight_details.flight_number}, "
                f"Status: {reservation.reservation_status}."
            )
            if send_notification_flag:
                await send_notification(email, message)
            return result
        return wrapper
    return decorator
