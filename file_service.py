from mcp.server.fastmcp import FastMCP
import csv
from pathlib import Path
import uuid

mcp = FastMCP("file_service",host="localhost", port=8000)

FILE = Path("C:\\Users\\ASUS\\OneDrive\\Documents\\mcp\\example1\\inventory.csv")


def ensure():
    """Create the CSV file with headers if it doesn't exist."""
    if not FILE.exists():
        with FILE.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "qty"])
            writer.writeheader()


@mcp.tool()
def read_csv() -> list[dict]:
    ensure()
    with FILE.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@mcp.tool()
def add_row(name: str, qty: int) -> dict:
    ensure()
    row = {
        "id": uuid.uuid4().hex[:6],
        "name": name,
        "qty": qty,
    }

    with FILE.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "qty"])
        writer.writerow(row)

    return row


@mcp.tool()
def update_qty(row_id: str, qty: int) -> str:
    ensure()

    rows = read_csv()

    for row in rows:
        if row["id"] == row_id:
            row["qty"] = str(qty)

    with FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "qty"])
        writer.writeheader()
        writer.writerows(rows)

    return "ok"


@mcp.tool()
def delete_row(row_id: str) -> str:
    ensure()

    rows = read_csv()
    rows = [row for row in rows if row["id"] != row_id]

    with FILE.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "name", "qty"])
        writer.writeheader()
        writer.writerows(rows)

    return "ok"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")