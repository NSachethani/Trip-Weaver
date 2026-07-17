import json
import urllib.request
import urllib.parse
from typing import Optional
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Hotel Service", port=8001)

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


def _only_name_address(data):
    """
    Convert full hotel response into only name and address.
    Supports both:
    1. {"hotels": [...]}
    2. [...]
    """

    if isinstance(data, dict) and "hotels" in data:
        hotels = data["hotels"]
    elif isinstance(data, list):
        hotels = data
    else:
        return data

    return [
        {
            "name": hotel.get("name"),
            "address": hotel.get("address")
        }
        for hotel in hotels
    ]


@mcp.tool()
def get_all_hotels() -> list[dict] | dict:
    """
    Retrieve all hotels with only name and address.
    """
    url = f"{BASE_URL}/hotels"
    data = _get_json(url)
    return _only_name_address(data)


@mcp.tool()
def search_hotels(
    city: str,
    checkIn: Optional[str] = None,
    checkOut: Optional[str] = None
) -> list[dict] | dict:
    """
    Search hotels by city.
    Returns only name and address.
    checkIn and checkOut are optional.
    """

    params = {
        "city": city
    }

    if checkIn:
        params["checkIn"] = checkIn

    if checkOut:
        params["checkOut"] = checkOut

    query_string = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/hotels/search?{query_string}"

    data = _get_json(url)
    return _only_name_address(data)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")