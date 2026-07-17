import requests
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Hotel Service", port=8003)

HOTEL_API_BASE = "https://standing-fish-574.convex.site/hotels"


def _fetch_json(url: str, params: Optional[dict] = None) -> Optional[Any]:
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


@mcp.tool()
def book_hotel(
    hotel_id: str,
    guest_name: str,
    guest_email: str,
    check_in_date: str,
    check_out_date: str,
    room_type: str,
) -> dict:
    """Book a hotel room.

    Args:
        hotel_id: ID of the hotel to book
        guest_name: Full name of the guest
        guest_email: Email of the guest
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        room_type: Type of room (single, double, suite)
    """

    payload = {
        "hotelId": hotel_id,
        "guestName": guest_name,
        "guestEmail": guest_email,
        "checkInDate": check_in_date,
        "checkOutDate": check_out_date,
        "roomType": room_type,
    }

    response = requests.post(
        f"{HOTEL_API_BASE}/book",
        json=payload
    )

    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
    