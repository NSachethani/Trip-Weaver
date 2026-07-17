import json
import urllib.request
import urllib.parse
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Flight Service", port=8002)

BASE_URL = "https://standing-fish-574.convex.site"


def _get_json(url: str):
    try:
        with urllib.request.urlopen(url, timeout=20) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)
    except Exception as e:
        return {
            "error": True,
            "message": str(e),
            "url": url
        }


def _only_airline_origin_destination(data):
    """
    Convert full flight response into only:
    airline, origin city, and destination city.

    Supports both:
    1. {"flights": [...]}
    2. [...]
    """

    if isinstance(data, dict) and "flights" in data:
        flights = data["flights"]
    elif isinstance(data, list):
        flights = data
    else:
        return data

    return [
        {
            "airline": flight.get("airline"),
            "originCity": flight.get("origin", {}).get("city"),
            "destinationCity": flight.get("destination", {}).get("city")
        }
        for flight in flights
    ]


@mcp.tool()
def get_all_flights() -> list[dict] | dict:
    """
    Retrieve all flights with only airline, origin city, and destination city.
    """
    url = f"{BASE_URL}/flights"
    data = _get_json(url)
    return _only_airline_origin_destination(data)


@mcp.tool()
def search_flights(
    origin: str,
    destination: str,
    date: Optional[str] = None
) -> list[dict] | dict:
    """
    Search flights by origin and destination.
    Returns only airline, origin city, and destination city.
    Date is optional.
    """

    params = {
        "origin": origin,
        "destination": destination
    }

    if date:
        params["date"] = date

    query_string = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/flights/search?{query_string}"

    data = _get_json(url)
    return _only_airline_origin_destination(data)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")