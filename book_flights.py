import requests
from typing import Any, Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("book_flights", port=8004)

BASE_URL = "https://standing-fish-574.convex.site"


def _fetch_json(url: str, params: Optional[dict] = None) -> Optional[Any]:
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


@mcp.tool()
def book_flight(
    flight_id: str,
    passenger_name: str,
    passenger_email: str,
) -> dict:
    """Book a flight ticket.

    Args:
        flight_id: ID of the flight to book
        passenger_name: Full name of the passenger
        passenger_email: Email of the passenger
    """
    payload = {
        "flightId": flight_id,
        "passengerName": passenger_name,
        "passengerEmail": passenger_email,
    }

    response = requests.post(f"{BASE_URL}/book", json=payload)
    response.raise_for_status()
    return response.json()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")